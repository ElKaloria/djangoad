import io
import uuid

from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User

from event_manager.models import Place


class EventStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    publish_at = models.DateTimeField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="events")

    rating = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=16, choices=EventStatus.choices, default=EventStatus.DRAFT)
    preview_image = models.ImageField(upload_to="events/previews/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def clean(self):
        if self.rating < 0 or self.rating > 25:
            raise ValueError("Rating must be in range 0..25")
        if self.starts_at > self.ends_at:
            raise ValueError("Event start date must be before end date")

    def save(self, *args, **kwargs):
        if self.preview_image:
            self.preview_image = resize_preview_image(self.preview_image)

        super().save(*args, **kwargs)


class EventImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="events/images/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)


def resize_preview_image(image_file, target_min_side=200):
    image = Image.open(image_file)
    width, height = image.size
    min_side = min(width, height)

    if min_side == target_min_side:
        return image_file

    scale = target_min_side / float(min_side)
    new_size = (int(width * scale), int(height * scale))
    resized = image.resize(new_size, Image.Resampling.LANCZOS)

    output = io.BytesIO()
    image_format = image.format or "JPEG"
    resized.save(output, format=image_format)
    output.seek(0)

    file_name = getattr(image_file, "name", f"{uuid.uuid4()}.jpg")

    return ContentFile(output.read(), name=file_name)
