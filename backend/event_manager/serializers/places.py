from django.contrib.gis.geos import Point
from rest_framework import serializers

from event_manager.models.places import Place


class PlaceSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True, required=True)
    longitude = serializers.FloatField(write_only=True, required=True)
    geo_location = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Place
        fields = ("id", "name", "latitude", "longitude", "geo_location")

    def get_geo_location(self, obj):
        return {"latitude": obj.geo_location.y, "longitude": obj.geo_location.x}

    def create(self, validated_data):
        latitude = validated_data.pop("latitude")
        longitude = validated_data.pop("longitude")
        validated_data["geo_location"] = Point(longitude, latitude, srid=4326)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        latitude = validated_data.pop("latitude", None)
        longitude = validated_data.pop("longitude", None)

        if latitude is not None and longitude is not None:
            validated_data["geo_location"] = Point(longitude, latitude, srid=4326)
            
        return super().update(instance, validated_data)
