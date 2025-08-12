from functools import wraps
from flask_login import current_user
from flask import abort

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            ok = True
            for r in roles:
                if r == "admin" and not current_user.is_admin:
                    ok = False
                if r == "pm" and not current_user.is_project_manager:
                    ok = False
                if r == "accounting" and not current_user.is_accounting:
                    ok = False
            if not ok:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator
