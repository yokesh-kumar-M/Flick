"""
Gateway API Proxy - Forwards requests to appropriate microservices.
This allows the frontend to call /proxy/auth/*, /proxy/catalog/*, etc.
"""
import requests
import json
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

SERVICE_MAP = {
    'auth': settings.AUTH_SERVICE_URL,
    'catalog': settings.CATALOG_SERVICE_URL,
    'access': settings.ACCESS_SERVICE_URL,
    'streaming': settings.STREAMING_SERVICE_URL,
    'recommendations': settings.RECOMMENDATION_SERVICE_URL,
    'notifications': settings.NOTIFICATION_SERVICE_URL,
}

# Connection pool
_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=2)
_session.mount('http://', adapter)


def _parse_json_body(request):
    """Parse JSON body from request, falling back to POST dict."""
    try:
        return json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return request.POST.dict()


def _is_multipart(request):
    return request.content_type and 'multipart' in request.content_type


@csrf_exempt
def proxy_view(request, service, path=''):
    """Proxy requests to microservices."""
    base_url = SERVICE_MAP.get(service)
    if not base_url:
        return JsonResponse({'error': f'Unknown service: {service}'}, status=404)

    if path.strip('/') == 'health':
        url = f"{base_url}/health/"
    else:
        url = f"{base_url}/api/{service}/{path}"
        if not url.endswith('/'):
            url += '/'

    # Forward headers
    headers = {}
    if request.META.get('HTTP_AUTHORIZATION'):
        headers['Authorization'] = request.META['HTTP_AUTHORIZATION']
    if request.content_type:
        headers['Content-Type'] = request.content_type

    # Forward cookies
    cookies = {}
    if request.COOKIES.get('access_token'):
        cookies['access_token'] = request.COOKIES['access_token']
    if request.COOKIES.get('refresh_token'):
        cookies['refresh_token'] = request.COOKIES['refresh_token']

    # Headers without Content-Type (for multipart — let requests set boundary)
    headers_no_ct = {k: v for k, v in headers.items() if k != 'Content-Type'}

    try:
        if request.method == 'GET':
            resp = _session.get(url, headers=headers, cookies=cookies,
                                params=request.GET.dict(), timeout=15)
        elif request.method == 'POST':
            if _is_multipart(request):
                resp = _session.post(url, headers=headers_no_ct, cookies=cookies,
                                     files=request.FILES, data=request.POST, timeout=30)
            else:
                resp = _session.post(url, headers=headers, cookies=cookies,
                                     json=_parse_json_body(request), timeout=15)
        elif request.method == 'PUT':
            resp = _session.put(url, headers=headers, cookies=cookies,
                                json=_parse_json_body(request), timeout=15)
        elif request.method == 'PATCH':
            if _is_multipart(request):
                resp = _session.patch(url, headers=headers_no_ct, cookies=cookies,
                                      files=request.FILES, data=request.POST, timeout=30)
            else:
                resp = _session.patch(url, headers=headers, cookies=cookies,
                                      json=_parse_json_body(request), timeout=15)
        elif request.method == 'DELETE':
            resp = _session.delete(url, headers=headers, cookies=cookies, timeout=15)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)

        # Build response
        django_response = HttpResponse(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )

        # Forward cookies from service response
        for cookie in resp.cookies:
            if not cookie.value or cookie.get('max-age') == 0 or (cookie.expires and cookie.expires < 0):
                django_response.delete_cookie(cookie.name, path='/', samesite='Lax')
            else:
                django_response.set_cookie(
                    cookie.name, cookie.value,
                    httponly=True, samesite='Lax', path='/',
                    max_age=cookie.get('max-age') or 86400
                )

        return django_response

    except requests.exceptions.ConnectionError:
        return JsonResponse({'error': f'Service {service} is unavailable'}, status=503)
    except requests.exceptions.Timeout:
        return JsonResponse({'error': f'Service {service} timed out'}, status=504)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
