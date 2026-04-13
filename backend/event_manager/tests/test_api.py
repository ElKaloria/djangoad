from datetime import timedelta
from io import BytesIO

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from openpyxl import Workbook
from rest_framework import status
from rest_framework.test import APITestCase

from event_manager.models.events import Event, EventStatus
from event_manager.models.places import Place

User = get_user_model()


class PlaceApiTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", password="admin", email="admin@example.com"
        )
        self.user = User.objects.create_user(
            username="user", password="user", email="user@example.com"
        )
        self.url = reverse("places-list")

    def test_place_create_allowed_only_for_superuser(self):
        payload = {"name": "Hall A", "latitude": 55.75, "longitude": 37.62}

        self.client.force_authenticate(self.user)
        resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.superuser)
        resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class EventApiTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", password="admin", email="admin@example.com"
        )
        self.user = User.objects.create_user(
            username="user", password="user", email="user@example.com"
        )
        self.place = Place.objects.create(name="Arena", geo_location=Point(37.62, 55.75, srid=4326))
        now = timezone.now()
        self.draft_event = Event.objects.create(
            name="Draft event",
            description="d",
            publish_at=now + timedelta(days=1),
            starts_at=now + timedelta(days=2),
            ends_at=now + timedelta(days=3),
            author=self.superuser,
            place=self.place,
            rating=10,
            status=EventStatus.DRAFT,
        )
        self.published_event = Event.objects.create(
            name="Published event",
            description="p",
            publish_at=now - timedelta(days=2),
            starts_at=now + timedelta(days=1),
            ends_at=now + timedelta(days=2),
            author=self.superuser,
            place=self.place,
            rating=15,
            status=EventStatus.PUBLISHED,
        )

    def test_regular_user_sees_only_published(self):
        self.client.force_authenticate(self.user)
        resp = self.client.get(reverse("events-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["id"], str(self.published_event.id))

    def test_superuser_sees_all(self):
        self.client.force_authenticate(self.superuser)
        resp = self.client.get(reverse("events-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 2)

    def test_export_xlsx(self):
        self.client.force_authenticate(self.superuser)
        resp = self.client.get(reverse("events-export-xlsx"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            resp["Content-Type"],
        )

    def test_import_xlsx_for_superuser(self):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(
            [
                "Название",
                "Описание",
                "Дата публикации",
                "Дата начала",
                "Дата завершения",
                "Место",
                "Координаты",
                "Рейтинг",
            ]
        )
        now = timezone.now()
        sheet.append(
            [
                "Imported event",
                "desc",
                now.isoformat(),
                (now + timedelta(days=1)).isoformat(),
                (now + timedelta(days=2)).isoformat(),
                "Imported place",
                "55.75,37.62",
                20,
            ]
        )
        stream = BytesIO()
        workbook.save(stream)
        stream.seek(0)
        uploaded = SimpleUploadedFile(
            "events.xlsx",
            stream.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        self.client.force_authenticate(self.superuser)
        resp = self.client.post(
            reverse("events-import-xlsx"),
            {"file": uploaded},
            format="multipart",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["imported"], 1)
        self.assertTrue(Event.objects.filter(name="Imported event").exists())
