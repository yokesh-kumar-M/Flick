import time
import uuid
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        response['X-Response-Time'] = str(duration)
        logger.info(f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s")
        return response


class HealthCheckBypassMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/health/'):
            return self.get_response(request)
        return self.get_response(request)


class ServiceCorrelationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request.request_id = request_id
        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        return response