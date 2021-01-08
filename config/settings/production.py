# -*- coding: utf-8 -*-
from .base import *

SENTRY_DSN = os.getenv('SENTRY_DSN')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'thenewboston'),
        'USER': os.getenv('POSTGRES_USER', 'thenewboston'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'thenewboston'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432')
    }
}

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.tornado import TornadoIntegration

    sentry_sdk.init(
        SENTRY_DSN,
        traces_sample_rate=1.0,
        integrations=[CeleryIntegration(), DjangoIntegration(), RedisIntegration(), TornadoIntegration()],
    )

DEBUG = False

INTERNAL_IPS = [
    '127.0.0.1',
]
