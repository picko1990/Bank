from django.urls import path
from .views import StatList
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path("api/", StatList.as_view(), name="stats_api"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
