from .models import Stat
from .serializers import StatSerializer
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication


class StatFilter(filters.FilterSet):
    start = filters.DateTimeFilter(field_name='date', lookup_expr='gte', label='start')
    end = filters.DateTimeFilter(field_name='date', lookup_expr='lte', label='end')


class StatList(generics.ListCreateAPIView):
    queryset = Stat.objects.cached()
    serializer_class = StatSerializer
    filterset_class = StatFilter
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None
