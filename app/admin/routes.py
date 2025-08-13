# app/admin/routes.py
from flask import render_template
from flask_login import login_required
from . import admin_bp
from ..utils.security import admin_required  # ensures only admins can access

@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    # Template path: app/admin/templates/admin/dashboard.html
    return render_template("admin/dashboard.html")
