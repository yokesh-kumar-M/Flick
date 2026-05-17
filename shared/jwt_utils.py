"""
Shared JWT utilities for Flick microservices.
"""
import jwt
import time
import os
import hashlib
import hmac
import logging

from .events import get_redis_client

logger = logging.getLogger(__name__)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

redis_client = get_redis_client()

def _required_secret(name, dev_default):
    value = os.environ.get(name, '')
    if value:
        return value
    if DEBUG:
        return dev_default
    raise RuntimeError(f'{name} must be set when DEBUG=False')


JWT_SECRET = _required_secret('JWT_SECRET_KEY', 'flick-jwt-secret-key-2026')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_LIFETIME = int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME', 30))  # minutes
REFRESH_TOKEN_LIFETIME = int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME', 1440))  # minutes
HMAC_SECRET = _required_secret('HMAC_SECRET', 'flick-hmac-secret-2026')
ACCESS_CODE_SECRET = _required_secret('ACCESS_CODE_SECRET', 'flick-access-code-secret-2026')


def create_access_token(user_id, username, is_admin=False, has_super_access=False):
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'has_super_access': has_super_access,
        'type': 'access',
        'iat': int(time.time()),
        'exp': int(time.time()) + (ACCESS_TOKEN_LIFETIME * 60),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'type': 'refresh',
        'iat': int(time.time()),
        'exp': int(time.time()) + (REFRESH_TOKEN_LIFETIME * 60),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)



# ── Token Blacklist (Redis-backed) ──────

def _make_jti(payload: dict) -> str:
    """Derive a unique key from the token payload (iat + user_id + type)."""
    return f"{payload.get('user_id')}:{payload.get('iat')}:{payload.get('type')}"


def blacklist_token(token: str) -> bool:
    """
    Invalidate a JWT immediately (e.g. on logout) using Redis SETEX.
    Returns True if successfully blacklisted, False if token was already invalid.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        return False

    exp = payload.get('exp')
    if not exp:
        return False

    ttl = exp - int(time.time())
    if ttl > 0:
        try:
            redis_client.setex(f"blacklist:{_make_jti(payload)}", ttl, "1")
        except Exception as e:
            # If Redis is unavailable we can't enforce a blacklist, but the
            # token will still expire naturally at `exp`.
            logger.warning(f"blacklist_token: Redis unavailable, token not blacklisted: {e}")
            return False
    return True


def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

    # Reject tokens that have been explicitly blacklisted. If Redis is down,
    # fail open so a cache outage doesn't take down authentication entirely
    # (tokens still expire at `exp`).
    try:
        if redis_client.exists(f"blacklist:{_make_jti(payload)}"):
            return None
    except Exception as e:
        logger.warning(f"decode_token: blacklist check skipped, Redis unavailable: {e}")
    return payload



def generate_access_code(user_id, movie_id):
    """Generate SHA-256 access code for a user-movie pair."""
    timestamp = str(int(time.time()))
    raw = f"{user_id}:{movie_id}:{ACCESS_CODE_SECRET}:{timestamp}"
    code_hash = hashlib.sha256(raw.encode()).hexdigest()[:12].upper()
    return code_hash, timestamp


def verify_access_code(code, user_id, movie_id, timestamp):
    """Verify an access code."""
    raw = f"{user_id}:{movie_id}:{ACCESS_CODE_SECRET}:{timestamp}"
    expected = hashlib.sha256(raw.encode()).hexdigest()[:12].upper()
    return hmac.compare_digest(code, expected)


def generate_signed_url(path, expiry_seconds=3600):
    """Generate HMAC signed URL for stream segments."""
    expiry = int(time.time()) + expiry_seconds
    message = f"{path}:{expiry}"
    signature = hmac.new(
        HMAC_SECRET.encode(), message.encode(), digestmod=hashlib.sha256
    ).hexdigest()
    return f"{path}?expires={expiry}&signature={signature}"


def verify_signed_url(path, expires, signature):
    """Verify HMAC signed URL."""
    if int(expires) < int(time.time()):
        return False
    message = f"{path}:{expires}"
    expected = hmac.new(
        HMAC_SECRET.encode(), message.encode(), digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
