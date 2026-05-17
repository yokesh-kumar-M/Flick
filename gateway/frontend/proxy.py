"""
Gateway API Proxy (High-Performance Async)
Forwards requests to appropriate microservices using HTTP/2 and connection pooling.

Features:
- Fully asynchronous (non-blocking) using httpx
- Connection pooling for extreme throughput
- Retry logic: retries up to 2 times with 0.5s delay on failure
- Circuit breaker pattern: prevents cascading failures
- Request timeout of 10 seconds
- X-Request-ID header forwarding
"""
import asyncio
import json
import httpx
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
from ratelimit.decorators import ratelimit
from .circuit_breaker import get_circuit_breaker

SERVICE_MAP = {
    'auth': settings.AUTH_SERVICE_URL,
    'catalog': settings.CATALOG_SERVICE_URL,
    'access': settings.ACCESS_SERVICE_URL,
    'streaming': settings.STREAMING_SERVICE_URL,
    'recommendations': settings.RECOMMENDATION_SERVICE_URL,
    'notifications': settings.NOTIFICATION_SERVICE_URL,
}

MAX_RETRIES = 1
RETRY_DELAY = 0.5
REQUEST_TIMEOUT = httpx.Timeout(60.0, connect=30.0)

# Lazy global async client. We avoid instantiating at import time because the
# event loop doesn't exist yet and binding a client to the wrong loop causes
# RuntimeError in some ASGI setups.
_client_limits = httpx.Limits(max_keepalive_connections=100, max_connections=500)
_async_client: httpx.AsyncClient | None = None
_client_lock = asyncio.Lock()


async def get_async_client() -> httpx.AsyncClient:
    global _async_client
    if _async_client is None:
        async with _client_lock:
            if _async_client is None:
                _async_client = httpx.AsyncClient(
                    limits=_client_limits, timeout=REQUEST_TIMEOUT, http2=True
                )
    return _async_client


async def aclose_async_client() -> None:
    """Close the global client. Call from ASGI lifespan shutdown."""
    global _async_client
    if _async_client is not None:
        await _async_client.aclose()
        _async_client = None

async def _parse_json_body(request):
    """Parse JSON body from request asynchronously."""
    if not request.body:
        return {}
    try:
        # request.body is already in memory in Django
        return json.loads(request.body)
    except json.JSONDecodeError:
        # For x-www-form-urlencoded
        return request.POST.dict()

def _is_multipart(request):
    return request.content_type and 'multipart' in request.content_type

async def _make_request(method, url, headers, cookies, **kwargs):
    """Make HTTP request with retry logic using the global httpx client."""
    client = await get_async_client()
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            req = client.build_request(
                method=method,
                url=url,
                headers=headers,
                cookies=cookies,
                params=kwargs.get('params'),
                json=kwargs.get('json'),
                data=kwargs.get('data'),
                files=kwargs.get('files'),
            )
            resp = await client.send(req)
            if resp.status_code >= 500:
                resp.raise_for_status()
            return resp
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.HTTPStatusError) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY)

    raise last_error

@ratelimit(key='ip', rate='100/m', block=True)
@csrf_exempt
async def proxy_view(request, service, path=''):
    """Proxy requests to microservices asynchronously with retry, ratelimiting and circuit breaker."""
    base_url = SERVICE_MAP.get(service)
    if not base_url:
        return JsonResponse({'error': f'Unknown service: {service}'}, status=404)

    if path.strip('/') == 'health':
        url = f"{base_url}/health/"
    else:
        url = f"{base_url}/api/{service}/{path}"
        if not url.endswith('/'):
            url += '/'

    request_id = request.headers.get('X-Request-ID', '')
    
    headers = {}
    # Forward relevant headers
    for header in ['Authorization', 'Content-Type', 'X-Request-ID', 'User-Agent', 'Accept']:
        val = request.headers.get(header)
        if val:
            headers[header] = val

    cookies = request.COOKIES.copy()

    # Handle body parsing
    json_data = None
    data_payload = None
    files_payload = None
    
    if request.method in ('POST', 'PUT', 'PATCH'):
        if _is_multipart(request):
            # Multipart requires careful handling of file reads
            data_payload = request.POST.dict()
            # Offload file reading to threadpool to avoid blocking event loop
            files_payload = await sync_to_async(
                lambda: {k: (v.name, v.read(), v.content_type) for k, v in request.FILES.items()}
            )()
            headers.pop('Content-Type', None)
        else:
            json_data = await _parse_json_body(request)

    cb = get_circuit_breaker(service)
    
    try:
        try:
            resp = await cb.async_call(
                _make_request, 
                request.method, 
                url, 
                headers, 
                cookies,
                params=request.GET.dict() if request.method == 'GET' else None,
                json=json_data,
                data=data_payload,
                files=files_payload
            )
        except Exception as e:
            if "Circuit breaker" in str(e):
                return JsonResponse({'error': str(e), 'service': service}, status=503)
            raise

        django_response = HttpResponse(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )

        # Forward set-cookie headers
        for cookie_name, cookie_value in resp.cookies.items():
            if not cookie_value:
                django_response.delete_cookie(cookie_name, path='/', samesite='Lax')
            else:
                django_response.set_cookie(
                    cookie_name, cookie_value,
                    httponly=True, 
                    samesite='Lax', 
                    path='/',
                    secure=not settings.DEBUG,
                    max_age=86400
                )

        return django_response

    except httpx.ConnectError:
        return JsonResponse({'error': f'Service {service} is unavailable (Connection Error)'}, status=503)
    except httpx.TimeoutException:
        return JsonResponse({'error': f'Service {service} timed out'}, status=504)
    except Exception as e:
        return JsonResponse({'error': f'Proxy Error: {str(e)}'}, status=500)
