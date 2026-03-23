import os
import glob
import re

SECURITY_SETTINGS = """
# PRODUCTION OPTIMIZATIONS AND SECURITY UPGRADES
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CACHE LAYER UPGRADE (Redis)
redis_url = os.environ.get('REDIS_URL')
if redis_url:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': redis_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'IGNORE_EXCEPTIONS': True,  # Keep running if Redis is down
            }
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

# DRF OPTIMIZATIONS
REST_FRAMEWORK.update({
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
})
if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append('rest_framework.renderers.BrowsableAPIRenderer')
"""

settings_files = glob.glob("*/[a-z]*_project/settings.py") + ["gateway/gateway_project/settings.py"]

for sf in settings_files:
    if not os.path.exists(sf):
        continue
    with open(sf, "r") as f:
        content = f.read()
    
    # Avoid double patching
    if "PRODUCTION OPTIMIZATIONS AND SECURITY UPGRADES" in content:
        continue
    
    # Patch CORS
    content = content.replace("CORS_ALLOW_ALL_ORIGINS = True", 
                              "CORS_ALLOW_ALL_ORIGINS = DEBUG\nCORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'https://flick.example.com').split(',')")
    
    # Ensure REST_FRAMEWORK exists before patching it
    if "REST_FRAMEWORK = {" not in content:
        content += "\nREST_FRAMEWORK = {}\n"
        
    with open(sf, "a") as f:
        f.write("\n" + SECURITY_SETTINGS + "\n")
    print(f"Upgraded {sf}")

