# app/admin/routes.py
from flask import render_template, abort
from flask_login import login_required, current_user

from . import admin_bp
from ..models import db  # ensure db exists

# Try to import models; if missing, fall back to None so the app can still boot
try:
    from ..models import User  # type: ignore
except Exception:
    User = None  # type: ignore
try:
    from ..models import Project  # type: ignore
except Exception:
    Project = None  # type: ignore
try:
    from ..models import WageRate  # type: ignore
except Exception:
    WageRate = None  # type: ignore

# Security decorator(s)
try:
    from ..utils.security import admin_required
except Exception:
    # Fallback: inline simple admin gate if utils/security isn't ready yet
    def admin_required(f):
        from functools import wraps
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            # basic checks: is_admin bool or roles_csv containing 'admin'
            is_admin = bool(getattr(current_user, "is_admin", False)) or (
                "admin" in (getattr(current_user, "roles_csv", "") or "")
            )
            if not is_admin:
                abort(403)
            return f(*args, **kwargs)
        return wrapper


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    totals = {
        "users": (User.query.count() if User else 0),
        "projects": (Project.query.count() if Project else 0),
        "wage_rates": (WageRate.query.count() if WageRate else 0),
    }
    return render_template("admin/dashboard.html", totals=totals)
