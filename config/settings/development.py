import iptools

from .base import *

SECRET_KEY = 'somesecret'
DEBUG = True

STATICFILES_DIRS = [
   os.path.join(BASE_DIR, 'static')
]

INTERNAL_IPS = iptools.IpRangeList(
    '10/8',
    '127/8',
    '172.16/12',
    '192.168/16'
)

INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
