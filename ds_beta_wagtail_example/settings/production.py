from __future__ import absolute_import, unicode_literals
from .base import *
import dj_database_url
import os


env = os.environ.copy()
SECRET_KEY = env['SECRET_KEY']
DATABASES['default'] =  dj_database_url.config()
    
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter'
]

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Allow all host headers
ALLOWED_HOSTS = ['*']

DEBUG = False

try:
    from .local import *
except ImportError:
    pass
