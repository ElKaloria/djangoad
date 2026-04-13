from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import User

from event_manager.services.weather_provider import get_weather_payload
from event_manager.models import (
    Place,
    Event,
    Weather,
    EventStatus
)


@shared_task
def publish_scheduled_events():
    events = Event.objects.filter(status=EventStatus.DRAFT, publish_at__lte=timezone.now())

    for event in events:
        event.status = EventStatus.PUBLISHED
        event.save(update_fields=["status", "updated_at"])
        send_event_published_email.delay(str(event.id))

    return events.count()


@shared_task
def send_event_published_email(event_id: str):
    event = Event.objects.get(id=event_id)
    event_author = event.author

    users = User.objects.all()
    users_email = [user.email for user in users]

    if not users:
        return 0

    subject = f"New event was created {event.name}",
    message = f"{event_author.username} creted new event {event.name} with description {event.description}"

    return send_mail(
        subject=subject,
        message=message,
        from_email=event_author.email,
        recipient_list=users_email,
        fail_silently=False,
    )


@shared_task
def refresh_weather():
    created = 0

    for place in Place.objects.all():
        payload = get_weather_payload()
        Weather.objects.create(place=place, **payload)
        created += 1
        
    return created
