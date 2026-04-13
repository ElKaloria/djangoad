import uuid

from django.contrib.gis.db import models


class Place(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    geo_location = models.PointField(srid=4326)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name