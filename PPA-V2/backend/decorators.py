from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def role_required(*roles):
    """Use on any route that only certain roles should reach, e.g. @role_required('admin')"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            if get_jwt().get("role") not in roles:
                return jsonify(error="Access denied for this role"), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator