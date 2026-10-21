from django.contrib import admin

from .models import BlogItem, CalendarSettings, Item

admin.site.register(Item)
admin.site.register(BlogItem)


@admin.register(CalendarSettings)
class CalendarSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "description": (
                    "These URLs power the Upcoming Events section on the main website. "
                    "Paste the public iCal link from Google Calendar "
                    "(Settings → Integrate calendar → Public URL to this calendar), "
                    "and the Google subscribe link for the “Add to Google Calendar” button."
                ),
                "fields": ("ics_url", "google_subscribe_url", "updated_at"),
            },
        ),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not CalendarSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
