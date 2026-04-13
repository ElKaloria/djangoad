import uuid

from django.db import models

from event_manager.models.places import Place


class Weather(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="weather_records")
    temperature = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    wind_speed = models.FloatField()
    wind_direction = models.CharField(max_length=16)
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-collected_at",)

