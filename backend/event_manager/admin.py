from django.contrib import admin

from event_manager.models import (
    Place,
    Event,
    EventImage,
    Weather
)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "geo_location")
    search_fields = ("name",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "publish_at", "starts_at", "ends_at", "rating", "place")
    list_filter = ("status", "place")
    search_fields = ("name", "description", "place__name")


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ("event", "created_at")


@admin.register(Weather)
class WeatherAdmin(admin.ModelAdmin):
    list_display = ("place", "temperature", "humidity", "pressure", "wind_speed", "collected_at")
    readonly_fields = (
        "place",
        "temperature",
        "humidity",
        "pressure",
        "wind_speed",
        "wind_direction",
        "collected_at",
    )

