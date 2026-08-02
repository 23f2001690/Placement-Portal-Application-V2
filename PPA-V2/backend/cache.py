import json
import redis
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from backend.config import Config

redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)

DEFAULT_TTL = 60  # seconds


def _build_key(prefix, per_user):
    key = f"{prefix}:{request.full_path}"
    if per_user:
        try:
            verify_jwt_in_request()
            key += f":user:{get_jwt_identity()}"
        except Exception:
            pass
    return key


def cached(prefix, ttl=DEFAULT_TTL, per_user=False):
    """
    Caches a GET endpoint's JSON response in Redis for `ttl` seconds.
    per_user=True folds the JWT identity into the key, for endpoints whose
    response differs per logged-in user (e.g. per-student eligibility flags).
    Call invalidate_prefix() on the same prefix from any route that changes
    the underlying data, so stale results don't linger until expiry.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = _build_key(prefix, per_user)
            cached_value = redis_client.get(key)
            if cached_value is not None:
                return jsonify(json.loads(cached_value)), 200

            result = fn(*args, **kwargs)
            body, status = result if isinstance(result, tuple) else (result, 200)

            if status == 200:
                redis_client.setex(key, ttl, body.get_data(as_text=True))

            return result
        return wrapper
    return decorator


def invalidate_prefix(prefix):
    """Deletes every cached key under a prefix. Call after any write that changes cached data."""
    for key in redis_client.scan_iter(match=f"{prefix}:*"):
        redis_client.delete(key)