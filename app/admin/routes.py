from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import admin_bp                      # <-- import the blueprint from __init__
from ..utils.security import admin_required
from ..models import db, User, Project, WageRate, ProjectAssignment, ChangeLog

# --- Dashboard ---------------------------------------------------------------
@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    active_projects = Project.query.filter_by(is_archived=False).order_by(Project.name).all()
    archived_projects = Project.query.filter_by(is_archived=True).order_by(Project.name).all()
    user_count = User.query.count()
    return render_template(
        "admin/dashboard.html",
        active_projects=active_projects,
        archived_projects=archived_projects,
        user_count=user_count,
    )

# (Keep the rest of your admin routes below; examples shown for continuity)

@admin_bp.route("/projects")
@login_required
@admin_required
def projects():
    active = Project.query.filter_by(is_archived=False).order_by(Project.name).all()
    archived = Project.query.filter_by(is_archived=True).order_by(Project.name).all()
    return render_template("admin/projects.html", active=active, archived=archived)

@admin_bp.route("/users")
@login_required
@admin_required
def users():
    items = User.query.order_by(User.email).all()
    return render_template("admin/users.html", users=items)

@admin_bp.route("/wages/add", methods=["POST"])
@login_required
@admin_required
def add_wage():
    user_id = request.form.get("user_id", type=int)
    rate = request.form.get("rate", type=float)
    effective = request.form.get("effective_date")  # expect YYYY-MM-DD
    if not (user_id and rate and effective):
        flash("User, rate, and effective date are required.", "warning")
        return redirect(url_for("admin.users"))
    wr = WageRate(user_id=user_id, hourly_rate=rate, effective_date=effective)
    db.session.add(wr)
    db.session.commit()
    flash("Wage rate added.", "success")
    return redirect(url_for("admin.users"))
