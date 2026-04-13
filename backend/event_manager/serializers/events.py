from django.db import transaction
from rest_framework import serializers

from event_manager.models.events import Event, EventImage
from event_manager.models.weathers import Weather
from event_manager.serializers.places import PlaceSerializer
from event_manager.serializers.weather import WeatherSerializer


class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ("id", "image", "created_at")


class EventSerializer(serializers.ModelSerializer):
    images = EventImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    place_data = PlaceSerializer(source="place", read_only=True)
    weather = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "description",
            "publish_at",
            "starts_at",
            "ends_at",
            "author",
            "place",
            "place_data",
            "rating",
            "status",
            "preview_image",
            "images",
            "uploaded_images",
            "weather",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("author", "created_at", "updated_at")

    def get_weather(self, obj):
        weather = (
            Weather.objects.filter(place=obj.place)
            .order_by("-collected_at")
            .first()
        )

        if not weather:
            return None

        return WeatherSerializer(weather).data

    def validate(self, attrs):
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))
        rating = attrs.get("rating", getattr(self.instance, "rating", 0))

        if starts_at and ends_at and starts_at > ends_at:
            raise serializers.ValidationError("Дата начала должна быть раньше даты окончания")
        if rating < 0 or rating > 25:
            raise serializers.ValidationError("Рейтинг должен быть в диапазоне 0..25")

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])
        validated_data["author"] = self.context["request"].user

        instance = super().create(validated_data)

        for img in uploaded_images:
            EventImage.objects.create(event=instance, image=img)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])

        instance = super().update(instance, validated_data)

        for img in uploaded_images:
            EventImage.objects.create(event=instance, image=img)
            
        return instance
