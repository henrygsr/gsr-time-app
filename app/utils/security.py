from functools import wraps
from flask import abort
from flask_login import current_user


def _forbid():
    # Consistent 403 without redirect loops (login gating should be added separately)
    abort(403)


def admin_required(f):
    """
    Gate a view to admins only.
    Use together with @login_required, e.g.:

        @login_required
        @admin_required
        def view(): ...
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            _forbid()
        if not getattr(current_user, "is_admin", False):
            _forbid()
        return f(*args, **kwargs)
    return wrapper


# Optional helpers if you want to gate other roles elsewhere in the app.
def accounting_required(f):
    """Allow accounting or admin."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            _forbid()
        if not (getattr(current_user, "is_accounting", False) or getattr(current_user, "is_admin", False)):
            _forbid()
        return f(*args, **kwargs)
    return wrapper


def project_manager_required(f):
    """Allow project managers or admin."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            _forbid()
        if not (getattr(current_user, "is_project_manager", False) or getattr(current_user, "is_admin", False)):
            _forbid()
        return f(*args, **kwargs)
    return wrapper
