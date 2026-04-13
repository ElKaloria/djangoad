from django.urls import include, path
from rest_framework.routers import DefaultRouter

from event_manager.api import EventViewSet, PlaceViewSet
from event_manager.api.auth import login

router = DefaultRouter()
router.register("places", PlaceViewSet, basename="places")
router.register("events", EventViewSet, basename="events")

urlpatterns = [
    path("auth/login/", login, name="auth-login"),
    path("", include(router.urls)),
]
