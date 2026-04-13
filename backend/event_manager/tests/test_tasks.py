from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.utils import timezone

from event_manager.models.events import Event, EventStatus
from event_manager.models.places import Place
from event_manager.models.weathers import Weather
from event_manager.tasks import publish_scheduled_events, refresh_weather, send_event_published_email

User = get_user_model()


class CeleryTasksTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", password="admin", email="admin@example.com"
        )
        self.place = Place.objects.create(name="Hall", geo_location=Point(37.62, 55.75, srid=4326))

    @patch("event_manager.tasks.send_event_published_email.delay")
    def test_publish_scheduled_events(self, mocked_delay):
        now = timezone.now()
        event = Event.objects.create(
            name="To publish",
            description="desc",
            publish_at=now - timedelta(minutes=1),
            starts_at=now + timedelta(days=1),
            ends_at=now + timedelta(days=2),
            author=self.superuser,
            place=self.place,
            rating=5,
            status=EventStatus.DRAFT,
        )

        result = publish_scheduled_events()
        event.refresh_from_db()

        self.assertEqual(result, 1)
        self.assertEqual(event.status, EventStatus.PUBLISHED)
        mocked_delay.assert_called_once_with(str(event.id))

    @patch("event_manager.tasks.get_weather_payload")
    def test_refresh_weather(self, mocked_weather_payload):
        mocked_weather_payload.return_value = {
            "temperature": 20.0,
            "humidity": 50.0,
            "pressure": 750.0,
            "wind_speed": 3.2,
            "wind_direction": "N",
        }
        Place.objects.create(name="Second hall", geo_location=Point(30.31, 59.93, srid=4326))

        created = refresh_weather()

        self.assertEqual(created, 2)
        self.assertEqual(Weather.objects.count(), 2)

    @patch("event_manager.tasks.send_mail")
    def test_send_event_published_email(self, mocked_send_mail):
        mocked_send_mail.return_value = 1
        now = timezone.now()
        event = Event.objects.create(
            name="Mail event",
            description="desc",
            publish_at=now,
            starts_at=now + timedelta(days=1),
            ends_at=now + timedelta(days=2),
            author=self.superuser,
            place=self.place,
            rating=8,
            status=EventStatus.PUBLISHED,
        )

        result = send_event_published_email(str(event.id))

        self.assertEqual(result, 1)
        mocked_send_mail.assert_called_once()
