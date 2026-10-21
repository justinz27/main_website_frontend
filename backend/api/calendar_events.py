"""Fetch and parse the public CPMSoc Google Calendar ICS feed."""

from __future__ import annotations

import logging
import re
import urllib.request
from datetime import date, datetime, time, timedelta, timezone
from html import unescape
from typing import Any
from zoneinfo import ZoneInfo

from dateutil.rrule import rrulestr
from django.core.cache import cache
from icalendar import Calendar

logger = logging.getLogger(__name__)

CACHE_KEY_PREFIX = "upcoming_events_v3"
STALE_CACHE_KEY_PREFIX = "upcoming_events_v3_stale"
CACHE_TTL_SECONDS = 6 * 60 * 60  # 6 hours
DEFAULT_LIMIT = 6
DEFAULT_TZ = ZoneInfo("Australia/Sydney")
FETCH_TIMEOUT_SECONDS = 20

_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")

_FREQ_LABELS = {
    "DAILY": "Daily",
    "WEEKLY": "Weekly",
    "MONTHLY": "Monthly",
    "YEARLY": "Yearly",
}


def _strip_html(value: str) -> str:
    text = _TAG_RE.sub(" ", unescape(value or ""))
    return _WHITESPACE_RE.sub(" ", text).strip()


def _as_aware_datetime(value: Any, is_end: bool = False) -> datetime | None:
    """Normalize icalendar DTSTART/DTEND values to timezone-aware UTC datetimes."""
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=DEFAULT_TZ).astimezone(timezone.utc)
        return value.astimezone(timezone.utc)

    if isinstance(value, date):
        # All-day: start at midnight local; ICS end is exclusive next-day midnight.
        local_date = value
        if is_end:
            local_date = local_date - timedelta(days=1)
            end_local = datetime.combine(local_date, time(23, 59, 59), tzinfo=DEFAULT_TZ)
            return end_local.astimezone(timezone.utc)
        start_local = datetime.combine(local_date, time.min, tzinfo=DEFAULT_TZ)
        return start_local.astimezone(timezone.utc)

    return None


def _to_iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _rrule_freq(component) -> str | None:
    rrule = component.get("rrule")
    if not rrule:
        return None
    freq = rrule.get("FREQ")
    if isinstance(freq, list):
        freq = freq[0] if freq else None
    if freq is None:
        return None
    return str(freq).upper()


def _recurrence_label(component) -> str | None:
    freq = _rrule_freq(component)
    if not freq:
        return None
    return _FREQ_LABELS.get(freq, freq.title())


def _instance_bounds(
    component, now: datetime
) -> tuple[datetime, datetime, str | None] | None:
    """
    Return (start, end, recurrence_label) for the next relevant occurrence.

    For RRULE series: first occurrence that has not yet ended.
    For one-off events: the DTSTART/DTEND window if still upcoming/in progress.
    """
    start_raw = component.get("dtstart")
    if start_raw is None:
        return None

    start = _as_aware_datetime(start_raw.dt, is_end=False)
    if start is None:
        return None

    end_raw = component.get("dtend")
    if end_raw is not None:
        end = _as_aware_datetime(end_raw.dt, is_end=True)
    else:
        duration_prop = component.get("duration")
        if duration_prop is not None:
            end = start + duration_prop.dt
        else:
            end = start + timedelta(hours=1)

    if end is None:
        return None

    duration = end - start
    recurrence = _recurrence_label(component)
    rrule = component.get("rrule")

    if rrule:
        try:
            rrule_str = rrule.to_ical().decode()
            # Keep dtstart timezone; dateutil preserves it on generated occurrences.
            rule = rrulestr(rrule_str, dtstart=start)
            # Include an occurrence that is currently in progress.
            next_start = rule.after(now - duration, inc=False)
            if next_start is None:
                return None
            if next_start.tzinfo is None:
                next_start = next_start.replace(tzinfo=start.tzinfo or DEFAULT_TZ)
            next_start = next_start.astimezone(timezone.utc)
            next_end = next_start + duration
            if next_end < now:
                return None
            return next_start, next_end, recurrence
        except Exception:
            logger.exception("Failed to expand RRULE for %s", component.get("summary"))
            return None

    if end < now:
        return None
    return start, end, None


def _event_to_dict(component, now: datetime) -> dict[str, Any] | None:
    bounds = _instance_bounds(component, now)
    if bounds is None:
        return None

    start, end, recurrence = bounds

    summary = str(component.get("summary", "") or "").strip()
    if not summary:
        return None

    start_raw = component.get("dtstart")
    all_day = isinstance(start_raw.dt, date) and not isinstance(start_raw.dt, datetime)
    location = str(component.get("location", "") or "").strip()
    description = _strip_html(str(component.get("description", "") or ""))

    return {
        "title": summary,
        "description": description,
        "location": location,
        "start": _to_iso_z(start),
        "end": _to_iso_z(end),
        "all_day": all_day,
        "recurrence": recurrence,
    }


def _calendar_config() -> tuple[str, str]:
    """Return (ics_url, google_subscribe_url) from Django admin Calendar settings."""
    from .models import (
        DEFAULT_CALENDAR_GOOGLE_SUBSCRIBE_URL,
        DEFAULT_CALENDAR_ICS_URL,
        CalendarSettings,
    )

    try:
        config = CalendarSettings.load()
        ics = (config.ics_url or "").strip()
        google = (config.google_subscribe_url or "").strip()
        if ics:
            return ics, google
    except Exception:
        # DB may be unavailable during migrate / first boot.
        logger.debug("CalendarSettings unavailable; using code defaults", exc_info=True)

    return DEFAULT_CALENDAR_ICS_URL, DEFAULT_CALENDAR_GOOGLE_SUBSCRIBE_URL


def _ics_url() -> str:
    return _calendar_config()[0]


def _cache_keys() -> tuple[str, str]:
    # Include URL so changing the feed does not serve a stale list.
    suffix = str(abs(hash(_ics_url())) % (10**8))
    return f"{CACHE_KEY_PREFIX}:{suffix}", f"{STALE_CACHE_KEY_PREFIX}:{suffix}"


def calendar_subscribe_links() -> dict[str, str]:
    ics, google = _calendar_config()
    return {
        "google": google,
        "ics": ics,
    }


def _fetch_ics_bytes() -> bytes:
    ics_url = _ics_url()
    if not ics_url:
        raise ValueError("Calendar ICS URL is not configured (set it in Django admin → Calendar settings)")
    request = urllib.request.Request(
        ics_url,
        headers={"User-Agent": "CPMSocWebsite/1.0 (upcoming-events)"},
    )
    with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
        return response.read()


def parse_upcoming_events(ics_bytes: bytes, *, limit: int = DEFAULT_LIMIT) -> list[dict[str, Any]]:
    calendar = Calendar.from_ical(ics_bytes)
    now = datetime.now(timezone.utc)
    events: list[dict[str, Any]] = []

    for component in calendar.walk():
        if component.name != "VEVENT":
            continue
        # Skip exception overrides that are not series masters; they are one-offs
        # without RRULE and are handled as normal timed events above.
        event = _event_to_dict(component, now)
        if event is None:
            continue
        events.append(event)

    events.sort(key=lambda e: e["start"])
    return events[:limit]


def get_upcoming_events(*, limit: int = DEFAULT_LIMIT) -> list[dict[str, Any]]:
    cache_key, stale_key = _cache_keys()
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        ics_bytes = _fetch_ics_bytes()
        events = parse_upcoming_events(ics_bytes, limit=limit)
        cache.set(cache_key, events, CACHE_TTL_SECONDS)
        cache.set(stale_key, events, None)
        return events
    except Exception:
        logger.exception("Failed to fetch or parse upcoming calendar events")
        stale = cache.get(stale_key)
        if stale is not None:
            return stale
        return []


def get_upcoming_events_payload(*, limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    return {
        "events": get_upcoming_events(limit=limit),
        "subscribe": calendar_subscribe_links(),
    }
