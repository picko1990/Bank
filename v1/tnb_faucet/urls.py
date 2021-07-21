from django.urls import path
from .views.tnb_faucet import faucet_view, API

urlpatterns = [
    path('', faucet_view, name='faucet'),
    path('api', API.as_view(), name='api'),
]
