import django_filters

from event_manager.models.events import Event
from event_manager.models.places import Place


class EventFilter(django_filters.FilterSet):
    starts_at_from = django_filters.IsoDateTimeFilter(field_name="starts_at", lookup_expr="gte")
    starts_at_to = django_filters.IsoDateTimeFilter(field_name="starts_at", lookup_expr="lte")
    ends_at_from = django_filters.IsoDateTimeFilter(field_name="ends_at", lookup_expr="gte")
    ends_at_to = django_filters.IsoDateTimeFilter(field_name="ends_at", lookup_expr="lte")
    rating_from = django_filters.NumberFilter(field_name="rating", lookup_expr="gte")
    rating_to = django_filters.NumberFilter(field_name="rating", lookup_expr="lte")
    place = django_filters.ModelMultipleChoiceFilter(queryset=Place.objects.all())

    class Meta:
        model = Event
        fields = (
            "starts_at_from",
            "starts_at_to",
            "ends_at_from",
            "ends_at_to",
            "rating_from",
            "rating_to",
            "place",
        )
