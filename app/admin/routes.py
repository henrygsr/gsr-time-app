from flask import render_template
from flask_login import login_required

# IMPORTANT: import the blueprint object defined in app/admin/__init__.py
from . import admin_bp

# Role checks
from ..utils.security import admin_required

# Minimal data for the dashboard (optional and safe if models are empty)
try:
    from ..extensions import db  # shared db instance
    from ..models.user import User
    from ..models.project import Project
    from ..models.wage import WageRate
except Exception:  # keep dashboard resilient if models move
    db = None
    User = Project = WageRate = None


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    """Simple admin landing page."""
    users = projects = wages = []
    try:
        if User:
            users = User.query.order_by(User.email.asc()).all()
        if Project:
            projects = Project.query.order_by(Project.name.asc()).all()
        if WageRate:
            wages = WageRate.query.order_by(WageRate.effective_date.desc()).limit(10).all()
    except Exception:
        # Don't fail the page just because a query blew up
        pass

    return render_template(
        "admin/dashboard.html",
        users=users,
        projects=projects,
        wages=wages,
    )
