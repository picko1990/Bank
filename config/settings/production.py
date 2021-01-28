# -*- coding: utf-8 -*-
from .base import *

SENTRY_DSN = os.getenv('SENTRY_DSN')

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

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

LOGGING = {
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'error.handler': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'error.log'),
            'formatter': 'verbose',
            'level': 'ERROR',
        },
        'warning.handler': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'warning.log'),
            'formatter': 'verbose',
            'level': 'WARNING',
        },
        'debug.handler': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'debug.log'),
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'basic_slack_admins': {
            'level': 'INFO',
            'class': 'config.helpers.basic_slack_logger.SlackExceptionHandler',
        },
        'slack_admins': {
            'level': 'ERROR',
            'class': 'config.helpers.slack_logger.SlackExceptionHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['slack_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'thenewboston': {
            'handlers': ['error.handler', 'warning.handler', 'basic_slack_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
        'faucet': {
            'handlers': [
                'error.handler', 'warning.handler',
                'debug.handler', 'basic_slack_admins'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
    'version': 1,
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
