from functools import wraps
from flask import abort
from flask_login import current_user


def _forbid():
    # Return a clean 403 (use @login_required separately when you want redirects)
    abort(403)


def _has_role(user, role: str) -> bool:
    """Map friendly role names to user flags. Admin is treated as a superset."""
    role = role.lower()
    if role in ("admin", "administrator"):
        return getattr(user, "is_admin", False)
    if role in ("accounting", "finance"):
        return getattr(user, "is_accounting", False) or getattr(user, "is_admin", False)
    if role in ("pm", "project_manager", "project-manager", "projectmanager"):
        return getattr(user, "is_project_manager", False) or getattr(user, "is_admin", False)
    return False


def roles_required(*roles):
    """
    Allow access if the current user has ANY of the given roles.
    If 'admin' is explicitly listed, the user must be admin.

    Example:
        @login_required
        @roles_required('accounting', 'pm')
        def view(): ...
    """
    if not roles:
        raise ValueError("roles_required needs at least one role name")

    wanted = tuple(r.lower() for r in roles)

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                _forbid()

            # If admin is explicitly required, enforce it strictly.
            if "admin" in wanted and not getattr(current_user, "is_admin", False):
                _forbid()
                # (no return needed; abort raises)

            # Otherwise allow if user has any wanted role or is admin.
            if getattr(current_user, "is_admin", False) or any(_has_role(current_user, r) for r in wanted):
                return f(*args, **kwargs)

            _forbid()
        return wrapper
    return decorator


def admin_required(f):
    """Admins only."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
            _forbid()
        return f(*args, **kwargs)
    return wrapper


def accounting_required(f):
    """Accounting or admin."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            _forbid()
        if not (getattr(current_user, "is_accounting", False) or getattr(current_user, "is_admin", False)):
            _forbid()
        return f(*args, **kwargs)
    return wrapper


def project_manager_required(f):
    """Project manager or admin."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            _forbid()
        if not (getattr(current_user, "is_project_manager", False) or getattr(current_user, "is_admin", False)):
            _forbid()
        return f(*args, **kwargs)
    return wrapper
