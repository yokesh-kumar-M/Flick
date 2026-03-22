import os
import time
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
import redis


REQUEST_COUNTER = {'count': 0}


def check_redis():
    try:
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url, socket_timeout=2, socket_connect_timeout=2)
        r.ping()
        return 'ok'
    except Exception as e:
        return f'error: {str(e)}'


def check_service(url):
    try:
        import requests
        response = requests.get(f"{url}/health/", timeout=2)
        return 'ok' if response.status_code == 200 else 'error'
    except Exception as e:
        return f'error: {str(e)}'


def health_check(request):
    REQUEST_COUNTER['count'] += 1
    
    dependencies = {
        'redis': check_redis(),
        'auth': check_service(settings.AUTH_SERVICE_URL),
        'catalog': check_service(settings.CATALOG_SERVICE_URL),
    }
    
    return JsonResponse({
        'status': 'ok',
        'service': 'gateway',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'dependencies': dependencies,
    })


def metrics(request):
    REQUEST_COUNTER['count'] += 1
    return JsonResponse({
        'requests': REQUEST_COUNTER['count'],
        'service': 'gateway',
    })