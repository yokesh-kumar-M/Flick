"""
Shared authentication middleware for Flick microservices.

Note: Currently unused — services use inline get_user_payload() helpers instead.
This is available for services that want middleware-based auth (add to MIDDLEWARE in settings).
"""
from functools import wraps
from django.http import JsonResponse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shared.jwt_utils import decode_token


class JWTAuthenticationMiddleware:
    """Middleware that extracts JWT from cookies/headers and attaches user info to request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = None

        # Check Authorization header first
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]

        # Fall back to cookie
        if not token:
            token = request.COOKIES.get('access_token')

        if token:
            payload = decode_token(token)
            if payload and payload.get('type') == 'access':
                request.user_id = payload.get('user_id')
                request.username = payload.get('username')
                request.is_admin = payload.get('is_admin', False)
                request.is_authenticated_user = True
            else:
                request.user_id = None
                request.username = None
                request.is_admin = False
                request.is_authenticated_user = False
        else:
            request.user_id = None
            request.username = None
            request.is_admin = False
            request.is_authenticated_user = False

        response = self.get_response(request)
        return response


def jwt_required(view_func):
    """Decorator that requires valid JWT authentication."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request, 'is_authenticated_user', False):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator that requires admin JWT authentication."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request, 'is_authenticated_user', False):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if not getattr(request, 'is_admin', False):
            return JsonResponse({'error': 'Admin access required'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper
