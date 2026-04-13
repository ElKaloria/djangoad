from rest_framework.viewsets import ModelViewSet

from event_manager.models.places import Place
from event_manager.permissions import IsSuperuserOrReadPublished
from event_manager.serializers.places import PlaceSerializer


class PlaceViewSet(ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = (IsSuperuserOrReadPublished,)
