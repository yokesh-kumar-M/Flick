import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

_secret = os.environ.get('SECRET_KEY', '')
if not _secret:
    if not DEBUG:
        raise ImproperlyConfigured('SECRET_KEY environment variable is required in production.')
    _secret = 'gateway-service-dev-secret-key-NOT-FOR-PRODUCTION'
SECRET_KEY = _secret
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
ALLOWED_HOSTS.append('.vercel.app')
env_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if env_render_host:
    ALLOWED_HOSTS.append(env_render_host)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        'OPTIONS': {
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'frontend',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'shared.middleware.RequestTimingMiddleware',
    'shared.middleware.ServiceCorrelationMiddleware',
]

ROOT_URLCONF = 'gateway_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3', conn_max_age=600)
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
}

CORS_ALLOWED_ORIGINS = [o.strip() for o in os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8000').split(',') if o.strip()]
CORS_ALLOW_CREDENTIALS = True

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SECURE_CONTENT_SECURITY_POLICY = {
        "default-src": "'self'",
        "script-src": "'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.gstatic.com",
        "style-src": "'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com",
        "font-src": "'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com",
        "img-src": "'self' data: blob: https:",
        "media-src": "'self' blob:",
        "connect-src": "'self'",
        "frame-ancestors": "'none'",
    }

SENTRY_DSN = os.environ.get('SENTRY_DSN', '')

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1 if not DEBUG else 1.0,
        environment='production' if not DEBUG else 'development',
        send_default_pii=False,
    )

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

def add_cache_headers(self, request, path, mode):
    return [('Cache-Control', 'public, max-age=31536000')]

WHITENOISE_MAX_AGE = 31536000
WHITENOISE_MIMETYPES = {
    '.mp4': 'video/mp4',
    '.m3u8': 'application/x-mpegURL',
    '.ts': 'video/MP2T',
    '.webm': 'video/webm',
}
WHITENOISE_ADD_HEADERS_FUNCTION = add_cache_headers

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

def _ensure_http(url):
    return url if url.startswith('http') else f'http://{url}'

AUTH_SERVICE_URL = _ensure_http(os.environ.get('AUTH_SERVICE_URL', 'http://localhost:8001'))
CATALOG_SERVICE_URL = _ensure_http(os.environ.get('CATALOG_SERVICE_URL', 'http://localhost:8002'))
ACCESS_SERVICE_URL = _ensure_http(os.environ.get('ACCESS_SERVICE_URL', 'http://localhost:8003'))
STREAMING_SERVICE_URL = _ensure_http(os.environ.get('STREAMING_SERVICE_URL', 'http://localhost:8004'))
RECOMMENDATION_SERVICE_URL = _ensure_http(os.environ.get('RECOMMENDATION_SERVICE_URL', 'http://localhost:8005'))
NOTIFICATION_SERVICE_URL = _ensure_http(os.environ.get('NOTIFICATION_SERVICE_URL', 'http://localhost:8006'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
        'json': {'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
        'json_console': {'class': 'logging.StreamHandler', 'formatter': 'json'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO'},
        'django.security': {'handlers': ['console'], 'level': 'WARNING'},
    },
}

RATE_LIMIT_CACHE = 'default'
USER_RATE_LIMIT = os.environ.get('USER_RATE_LIMIT', '100/hour')

import sys
sys.path.insert(0, str(BASE_DIR.parent / 'shared'))
sys.path.insert(0, str(BASE_DIR.parent))
