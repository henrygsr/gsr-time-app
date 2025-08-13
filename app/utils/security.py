# app/utils/security.py
from functools import wraps
from flask import abort
from flask_login import current_user

def _has_role(user, role_name: str) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False

    # Common patterns: boolean is_admin, single 'role', list/relationship 'roles', CSV 'roles_csv'
    if role_name == "admin" and getattr(user, "is_admin", False):
        return True

    single = getattr(user, "role", None)
    if isinstance(single, str) and single == role_name:
        return True

    roles_csv = getattr(user, "roles_csv", None)
    if isinstance(roles_csv, str) and role_name in [r.strip() for r in roles_csv.split(",") if r.strip()]:
        return True

    roles = getattr(user, "roles", None)
    if roles is not None:
        try:
            # works for relationship of Role objects (with .name) or list of strings
            return any(getattr(r, "name", r) == role_name for r in roles)
        except TypeError:
            pass

    return False

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not getattr(current_user, "is_authenticated", False):
                abort(403)
            if not any(_has_role(current_user, r) for r in roles):
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not getattr(current_user, "is_authenticated", False) or not _has_role(current_user, "admin"):
            abort(403)
        return f(*args, **kwargs)
    return wrapper
