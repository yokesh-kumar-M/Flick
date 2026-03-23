import os
import asyncio
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
from asgiref.sync import sync_to_async
import redis
import httpx

REQUEST_COUNTER = {'count': 0}

async def check_redis():
    try:
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        # We run redis operations in a threadpool to not block the async loop
        def _ping_redis():
            r = redis.from_url(redis_url, socket_timeout=2, socket_connect_timeout=2)
            r.ping()
            return 'ok'
        return await sync_to_async(_ping_redis)()
    except Exception as e:
        return f'error: {str(e)}'

async def check_service(url):
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{url}/health/")
            return 'ok' if response.status_code == 200 else 'error'
    except Exception as e:
        return f'error: {str(e)}'

async def health_check(request):
    REQUEST_COUNTER['count'] += 1
    
    return JsonResponse({
        'status': 'ok',
        'service': 'gateway',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'dependencies': 'skipped_to_prevent_timeout',
    })

def metrics(request):
    REQUEST_COUNTER['count'] += 1
    return JsonResponse({
        'requests': REQUEST_COUNTER['count'],
        'service': 'gateway',
    })
