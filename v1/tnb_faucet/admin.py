from django.contrib import admin

from .models.tnb_faucet import FaucetModel, FaucetOption, PostModel

admin.site.register(FaucetModel)
admin.site.register(FaucetOption)
admin.site.register(PostModel)
