"""
Shared service communication client for Flick microservices.
"""
import requests
import os
import logging
from requests.adapters import HTTPAdapter

from .events import event_bus

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = float(os.environ.get('SERVICE_REQUEST_TIMEOUT', '3'))
DEFAULT_RETRIES = int(os.environ.get('SERVICE_REQUEST_RETRIES', '0'))
NOTIFICATION_TIMEOUT = float(os.environ.get('NOTIFICATION_REQUEST_TIMEOUT', '1'))
SERVICE_AUTH_TOKEN = os.environ.get('SERVICE_AUTH_TOKEN', '')

# Service registry
def _ensure_http(url):
    return url if url.startswith('http') else f'http://{url}'

SERVICE_URLS = {
    'gateway': _ensure_http(os.environ.get('GATEWAY_URL', 'http://localhost:8000')),
    'auth': _ensure_http(os.environ.get('AUTH_SERVICE_URL', 'http://localhost:8001')),
    'catalog': _ensure_http(os.environ.get('CATALOG_SERVICE_URL', 'http://localhost:8002')),
    'access': _ensure_http(os.environ.get('ACCESS_SERVICE_URL', 'http://localhost:8003')),
    'streaming': _ensure_http(os.environ.get('STREAMING_SERVICE_URL', 'http://localhost:8004')),
    'recommendation': _ensure_http(os.environ.get('RECOMMENDATION_SERVICE_URL', 'http://localhost:8005')),
    'notification': _ensure_http(os.environ.get('NOTIFICATION_SERVICE_URL', 'http://localhost:8006')),
}

# Connection pooling
_sessions = {}


def get_session(service_name):
    """Get or create a requests session for connection pooling."""
    if service_name not in _sessions:
        session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=DEFAULT_RETRIES,
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        _sessions[service_name] = session
    return _sessions[service_name]


def service_request(service_name, method, path, **kwargs):
    """Make a request to another microservice."""
    base_url = SERVICE_URLS.get(service_name)
    if not base_url:
        raise ValueError(f"Unknown service: {service_name}")

    url = f"{base_url}{path}"
    session = get_session(service_name)
    timeout = kwargs.pop('timeout', DEFAULT_TIMEOUT)

    try:
        response = session.request(method, url, timeout=timeout, **kwargs)
        return response
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error to {service_name} at {url}")
        return None
    except requests.exceptions.Timeout:
        logger.error(f"Timeout connecting to {service_name} at {url}")
        return None


def send_notification(user_id, title, message, notification_type='info', link=''):
    """Send a notification to a user via the event bus (asynchronous)."""
    try:
        event_bus.publish('notifications', 'send_notification', {
            'user_id': user_id,
            'title': title,
            'message': message,
            'notification_type': notification_type,
            'link': link,
        })
        return True
    except Exception as e:
        logger.error(f"Failed to publish notification event: {e}")
        return False
