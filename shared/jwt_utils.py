"""
Shared JWT utilities for Flick microservices.
"""
import jwt
import time
import os
import hashlib
import hmac

JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'flick-jwt-secret-key-2026')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_LIFETIME = int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME', 30))  # minutes
REFRESH_TOKEN_LIFETIME = int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME', 1440))  # minutes
HMAC_SECRET = os.environ.get('HMAC_SECRET', 'flick-hmac-secret-2026')
ACCESS_CODE_SECRET = os.environ.get('ACCESS_CODE_SECRET', 'flick-access-code-secret-2026')


def create_access_token(user_id, username, is_admin=False):
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
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



# ── Token Blacklist (in-process; survives only while server is running) ──────
# For production, replace with a Redis-backed store.
_blacklisted_tokens: dict[str, int] = {}   # jti_key → expiry timestamp


def _make_jti(payload: dict) -> str:
    """Derive a unique key from the token payload (iat + user_id + type)."""
    return f"{payload.get('user_id')}:{payload.get('iat')}:{payload.get('type')}"


def blacklist_token(token: str) -> bool:
    """
    Invalidate a JWT immediately (e.g. on logout).
    Returns True if successfully blacklisted, False if token was already invalid.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        jti = _make_jti(payload)
        _blacklisted_tokens[jti] = payload['exp']
        _purge_expired_blacklist()
        return True
    except jwt.InvalidTokenError:
        return False


def _purge_expired_blacklist():
    """Remove expired entries from the blacklist to prevent memory growth."""
    now = int(time.time())
    expired_keys = [k for k, exp in _blacklisted_tokens.items() if exp < now]
    for k in expired_keys:
        del _blacklisted_tokens[k]


def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # Reject tokens that have been explicitly blacklisted (e.g. logged out)
        if _make_jti(payload) in _blacklisted_tokens:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None



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
