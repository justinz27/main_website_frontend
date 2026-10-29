from django.core.cache import cache
from django.db import models

# Seed / fallback values used only until Calendar settings are saved in admin.
DEFAULT_CALENDAR_ICS_URL = (
    "https://calendar.google.com/calendar/ical/"
    "c_f45f37c8d33e60ce018fc0ee627247d7f782741f2fb6dcb21b09ee8b4eaf5a1c"
    "%40group.calendar.google.com/public/basic.ics"
)
DEFAULT_CALENDAR_GOOGLE_SUBSCRIBE_URL = (
    "https://calendar.google.com/calendar/u/0/r?cid="
    "Y19mNDVmMzdjOGQzM2U2MGNlMDE4ZmMwZWU2MjcyNDdkN2Y3ODI3NDFmMmZiNmRjYjIxYjA5ZWU4YjRlYWY1YTFj"
    "QGdyb3VwLmNhbGVuZGFyLmdvb2dsZS5jb20"
)

# Create your models here.

# This is for all the blog items
class BlogItem(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    blog_name = models.CharField(max_length=200, unique=True)
    date_published = models.DateField()
    author = models.CharField(max_length=100)
    tldr_text = models.TextField()
    tags = models.JSONField(default=list)
    tile_image = models.URLField()
    blog_image = models.URLField()
    text = models.TextField()

    def __str__(self):
        return self.blog_name


class CalendarSettings(models.Model):
    """Singleton config for the public calendar — edit in Django admin."""

    ics_url = models.URLField(
        max_length=1000,
        help_text="Public iCal (.ics) feed URL used to load events and for “Add to other calendar”.",
    )
    google_subscribe_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="Google Calendar “Add calendar” / subscribe link shown on the website.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Calendar settings"
        verbose_name_plural = "Calendar settings"

    def __str__(self):
        return "Calendar settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        # Drop cached event lists so the next request uses the new URLs.
        cache.clear()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls) -> "CalendarSettings":
        defaults = {
            "ics_url": DEFAULT_CALENDAR_ICS_URL,
            "google_subscribe_url": DEFAULT_CALENDAR_GOOGLE_SUBSCRIBE_URL,
        }
        obj, _ = cls.objects.get_or_create(pk=1, defaults=defaults)
        return obj
