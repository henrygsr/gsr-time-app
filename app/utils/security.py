from functools import wraps
from flask import abort, redirect, request, url_for
from flask_login import current_user

def _user_has_role(user, role: str) -> bool:
    # Map role labels to boolean flags on the User model
    if role == "admin":
        return bool(getattr(user, "is_admin", False))
    if role in ("project_manager", "pm"):
        return bool(getattr(user, "is_project_manager", False))
    if role in ("accounting", "accountant"):
        return bool(getattr(user, "is_accounting", False))
    return False

def admin_required(fn):
    """Allow only users with is_admin=True."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.path))
        if not _user_has_role(current_user, "admin"):
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

def roles_required(*roles):
    """
    Allow if the current user has ANY of the supplied roles.
    Example: @roles_required("admin", "project_manager")
    """
    norm_roles = tuple(r.lower() for r in roles)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login", next=request.path))
            if not any(_user_has_role(current_user, r) for r in norm_roles):
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
