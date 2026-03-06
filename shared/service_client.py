"""
Shared service communication client for Flick microservices.
"""
import requests
import os
import logging

logger = logging.getLogger(__name__)

# Service registry
SERVICE_URLS = {
    'gateway': os.environ.get('GATEWAY_URL', 'http://localhost:8000'),
    'auth': os.environ.get('AUTH_SERVICE_URL', 'http://localhost:8001'),
    'catalog': os.environ.get('CATALOG_SERVICE_URL', 'http://localhost:8002'),
    'access': os.environ.get('ACCESS_SERVICE_URL', 'http://localhost:8003'),
    'streaming': os.environ.get('STREAMING_SERVICE_URL', 'http://localhost:8004'),
    'recommendation': os.environ.get('RECOMMENDATION_SERVICE_URL', 'http://localhost:8005'),
    'notification': os.environ.get('NOTIFICATION_SERVICE_URL', 'http://localhost:8006'),
}

# Connection pooling
_sessions = {}


def get_session(service_name):
    """Get or create a requests session for connection pooling."""
    if service_name not in _sessions:
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3
        )
        session.mount('http://', adapter)
        _sessions[service_name] = session
    return _sessions[service_name]


def service_request(service_name, method, path, **kwargs):
    """Make a request to another microservice."""
    base_url = SERVICE_URLS.get(service_name)
    if not base_url:
        raise ValueError(f"Unknown service: {service_name}")

    url = f"{base_url}{path}"
    session = get_session(service_name)
    timeout = kwargs.pop('timeout', 10)

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
    """Send a notification to a user via the notification service."""
    try:
        response = service_request(
            'notification', 'POST',
            '/api/notifications/create/',
            json={
                'user_id': user_id,
                'title': title,
                'message': message,
                'notification_type': notification_type,
                'link': link,
            },
            timeout=5,
        )
        if response and response.status_code == 201:
            return True
        logger.warning(f"Notification send failed: {response.status_code if response else 'no response'}")
        return False
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return False
