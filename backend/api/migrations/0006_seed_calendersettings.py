# Generated manually — seed singleton Calendar settings.

from django.db import migrations

DEFAULT_ICS_URL = (
    "https://calendar.google.com/calendar/ical/"
    "c_f45f37c8d33e60ce018fc0ee627247d7f782741f2fb6dcb21b09ee8b4eaf5a1c"
    "%40group.calendar.google.com/public/basic.ics"
)
DEFAULT_GOOGLE_SUBSCRIBE_URL = (
    "https://calendar.google.com/calendar/u/0/r?cid="
    "Y19mNDVmMzdjOGQzM2U2MGNlMDE4ZmMwZWU2MjcyNDdkN2Y3ODI3NDFmMmZiNmRjYjIxYjA5ZWU4YjRlYWY1YTFj"
    "QGdyb3VwLmNhbGVuZGFyLmdvb2dsZS5jb20"
)


def seed_calendar_settings(apps, schema_editor):
    CalendarSettings = apps.get_model("api", "CalendarSettings")
    if CalendarSettings.objects.exists():
        return
    CalendarSettings.objects.create(
        pk=1,
        ics_url=DEFAULT_ICS_URL,
        google_subscribe_url=DEFAULT_GOOGLE_SUBSCRIBE_URL,
    )


def unseed_calendar_settings(apps, schema_editor):
    CalendarSettings = apps.get_model("api", "CalendarSettings")
    CalendarSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_calendersettings"),
    ]

    operations = [
        migrations.RunPython(seed_calendar_settings, unseed_calendar_settings),
    ]
