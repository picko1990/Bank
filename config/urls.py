from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from v1.accounts.urls import router as accounts_router
from v1.bank_transactions.urls import router as bank_transactions_router
from v1.banks.urls import router as banks_router
from v1.blocks.urls import router as blocks_router
from v1.clean.urls import router as clean_router
from v1.confirmation_blocks.urls import router as confirmation_blocks_router
from v1.connection_requests.urls import router as connection_requests_router
from v1.crawl.urls import router as crawl_router
from v1.invalid_blocks.urls import router as invalid_blocks_router
from v1.self_configurations.urls import router as self_configurations_router
from v1.status_updates.urls import router as status_updates_router
from v1.validator_confirmation_services.urls import router as validator_confirmation_services_router
from v1.validators.urls import router as validators_router

admin.site.index_title = 'Admin'
admin.site.site_header = 'Bank'
admin.site.site_title = 'Bank'

schema_view = get_schema_view(
    openapi.Info(
        title='Bank API',
        default_version='v1',
        description='API documentation for thenewboston digital currency network Bank node.',
        terms_of_service='https://www.google.com/policies/terms/',
        contact=openapi.Contact(email='bucky@thenewboston.com'),
        license=openapi.License(name='MIT License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    # Core
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('faucet/', include('v1.tnb_faucet.urls')),
    path('stats/', include('v1.tnb_stats.urls')),

    # OpenAPI (Swagger)
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

router = DefaultRouter(trailing_slash=False)

router.registry.extend(accounts_router.registry)
router.registry.extend(bank_transactions_router.registry)
router.registry.extend(banks_router.registry)
router.registry.extend(blocks_router.registry)
router.registry.extend(clean_router.registry)
router.registry.extend(confirmation_blocks_router.registry)
router.registry.extend(connection_requests_router.registry)
router.registry.extend(crawl_router.registry)
router.registry.extend(invalid_blocks_router.registry)
router.registry.extend(self_configurations_router.registry)
router.registry.extend(status_updates_router.registry)
router.registry.extend(validator_confirmation_services_router.registry)
router.registry.extend(validators_router.registry)

urlpatterns += router.urls

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
