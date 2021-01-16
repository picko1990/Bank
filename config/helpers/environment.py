import os

ENVIRONMENT = os.environ.get('DJANGO_APPLICATION_ENVIRONMENT', 'development')

if ENVIRONMENT == 'development':
    SETTINGS_MODULE = 'config.settings.development'

if ENVIRONMENT == 'local':
    SETTINGS_MODULE = 'config.settings.local'

if ENVIRONMENT == 'postgres_local':
    SETTINGS_MODULE = 'config.settings.local'

if ENVIRONMENT == 'production':
    SETTINGS_MODULE = 'config.settings.production'

if ENVIRONMENT == 'staging':
    SETTINGS_MODULE = 'config.settings.staging'

if ENVIRONMENT == 'test':
    SETTINGS_MODULE = 'config.settings.test'
