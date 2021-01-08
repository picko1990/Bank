from django.contrib import admin

from .models.tnb_faucet import FaucetModel, FaucetOption

admin.site.register(FaucetModel)
admin.site.register(FaucetOption)
