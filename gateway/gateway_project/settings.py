import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

_secret = os.environ.get('SECRET_KEY', '')
if not _secret:
    if not DEBUG:
        raise ImproperlyConfigured('SECRET_KEY environment variable is required in production.')
    _secret = 'gateway-service-dev-secret-key-NOT-FOR-PRODUCTION'
SECRET_KEY = _secret
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
env_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if env_render_host:
    ALLOWED_HOSTS.append(env_render_host)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
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
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

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

# Service URLs for API proxy
def _ensure_http(url):
    return url if url.startswith('http') else f'http://{url}'

AUTH_SERVICE_URL = _ensure_http(os.environ.get('AUTH_SERVICE_URL', 'http://localhost:8001'))
CATALOG_SERVICE_URL = _ensure_http(os.environ.get('CATALOG_SERVICE_URL', 'http://localhost:8002'))
ACCESS_SERVICE_URL = _ensure_http(os.environ.get('ACCESS_SERVICE_URL', 'http://localhost:8003'))
STREAMING_SERVICE_URL = _ensure_http(os.environ.get('STREAMING_SERVICE_URL', 'http://localhost:8004'))
RECOMMENDATION_SERVICE_URL = _ensure_http(os.environ.get('RECOMMENDATION_SERVICE_URL', 'http://localhost:8005'))
NOTIFICATION_SERVICE_URL = _ensure_http(os.environ.get('NOTIFICATION_SERVICE_URL', 'http://localhost:8006'))

import sys
sys.path.insert(0, str(BASE_DIR.parent / 'shared'))
sys.path.insert(0, str(BASE_DIR.parent))
