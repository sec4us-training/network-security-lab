from django.contrib import admin

from .models import Event, Host


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ("name", "ip", "zone", "role")
    list_filter = ("zone",)
    search_fields = ("name", "ip", "role")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("created", "host", "severity", "message")
    list_filter = ("severity", "host")
    search_fields = ("message",)
