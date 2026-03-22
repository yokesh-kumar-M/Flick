"""
Gateway API Proxy - Forwards requests to appropriate microservices.
This allows the frontend to call /proxy/auth/*, /proxy/catalog/*, etc.

Features:
- Retry logic: retries up to 2 times with 0.5s delay on failure
- Circuit breaker pattern: after 5 consecutive failures, marks service as 'open' for 30s
- Request timeout of 10 seconds
- X-Request-ID header forwarding
"""
import time
import requests
import json
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .circuit_breaker import get_circuit_breaker


SERVICE_MAP = {
    'auth': settings.AUTH_SERVICE_URL,
    'catalog': settings.CATALOG_SERVICE_URL,
    'access': settings.ACCESS_SERVICE_URL,
    'streaming': settings.STREAMING_SERVICE_URL,
    'recommendations': settings.RECOMMENDATION_SERVICE_URL,
    'notifications': settings.NOTIFICATION_SERVICE_URL,
}

MAX_RETRIES = 2
RETRY_DELAY = 0.5
REQUEST_TIMEOUT = 10

_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=0)
_session.mount('http://', adapter)


def _parse_json_body(request):
    """Parse JSON body from request, falling back to POST dict."""
    try:
        return json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return request.POST.dict()


def _is_multipart(request):
    return request.content_type and 'multipart' in request.content_type


def _make_request(method, url, headers, cookies, timeout=REQUEST_TIMEOUT, **kwargs):
    """Make HTTP request with retry logic."""
    last_error = None
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            if method == 'GET':
                resp = _session.get(url, headers=headers, cookies=cookies, params=kwargs.get('params'), timeout=timeout)
            elif method == 'POST':
                if kwargs.get('files'):
                    resp = _session.post(url, headers=headers, cookies=cookies, files=kwargs.get('files'), data=kwargs.get('data'), timeout=timeout)
                else:
                    resp = _session.post(url, headers=headers, cookies=cookies, json=kwargs.get('json'), timeout=timeout)
            elif method == 'PUT':
                resp = _session.put(url, headers=headers, cookies=cookies, json=kwargs.get('json'), timeout=timeout)
            elif method == 'PATCH':
                if kwargs.get('files'):
                    resp = _session.patch(url, headers=headers, cookies=cookies, files=kwargs.get('files'), data=kwargs.get('data'), timeout=timeout)
                else:
                    resp = _session.patch(url, headers=headers, cookies=cookies, json=kwargs.get('json'), timeout=timeout)
            elif method == 'DELETE':
                resp = _session.delete(url, headers=headers, cookies=cookies, timeout=timeout)
            else:
                raise ValueError(f"Unknown method: {method}")
            return resp
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    
    raise last_error


@csrf_exempt
def proxy_view(request, service, path=''):
    """Proxy requests to microservices with retry and circuit breaker."""
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
    if request.META.get('HTTP_AUTHORIZATION'):
        headers['Authorization'] = request.META['HTTP_AUTHORIZATION']
    if request.content_type:
        headers['Content-Type'] = request.content_type
    if request_id:
        headers['X-Request-ID'] = request_id

    cookies = {}
    if request.COOKIES.get('access_token'):
        cookies['access_token'] = request.COOKIES['access_token']
    if request.COOKIES.get('refresh_token'):
        cookies['refresh_token'] = request.COOKIES['refresh_token']

    headers_no_ct = {k: v for k, v in headers.items() if k != 'Content-Type'}

    cb = get_circuit_breaker(service)
    
    try:
        try:
            resp = cb.call(_make_request, request.method, url, headers, cookies, REQUEST_TIMEOUT,
                          params=request.GET.dict() if request.method == 'GET' else None,
                          json=_parse_json_body(request) if request.method in ('POST', 'PUT', 'PATCH') and not _is_multipart(request) else None,
                          files=request.FILES if request.FILES else None,
                          data=request.POST if _is_multipart(request) and not request.FILES else None)
        except Exception as e:
            if "Circuit breaker" in str(e):
                return JsonResponse({'error': str(e), 'service': service}, status=503)
            raise

        django_response = HttpResponse(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )

        import time as time_module
        for cookie in resp.cookies:
            if not cookie.value or (cookie.expires and cookie.expires < 0):
                django_response.delete_cookie(cookie.name, path='/', samesite='Lax')
            else:
                max_age = max(0, int(cookie.expires - time_module.time())) if cookie.expires else 86400
                django_response.set_cookie(
                    cookie.name, cookie.value,
                    httponly=True, samesite='Lax', path='/',
                    max_age=max_age
                )

        return django_response

    except requests.exceptions.ConnectionError:
        return JsonResponse({'error': f'Service {service} is unavailable'}, status=503)
    except requests.exceptions.Timeout:
        return JsonResponse({'error': f'Service {service} timed out'}, status=504)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)