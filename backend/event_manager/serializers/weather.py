from rest_framework import serializers

from event_manager.models.weathers import Weather


class WeatherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Weather
        fields = (
            "id",
            "temperature",
            "humidity",
            "pressure",
            "wind_speed",
            "wind_direction",
            "collected_at",
        )