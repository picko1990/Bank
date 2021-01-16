from django.urls import path

from .views.tnb_faucet import faucet_view

urlpatterns = [
    path('', faucet_view, name='faucet')
]
