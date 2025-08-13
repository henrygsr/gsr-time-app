# app/admin/routes.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from . import admin_bp  # defined in app/admin/__init__.py
from ..utils.security import roles_required  # requires role check ("admin")
from ..models import db, User, Project, WageRate
from ..models.settings import AppSetting, GlobalSettings


@admin_bp.route("/")
@login_required
@roles_required("admin")
def dashboard():
    users = User.query.order_by(User.created_at.desc()).limit(10).all() if hasattr(User, "created_at") else User.query.limit(10).all()
    projects = Project.query.limit(10).all()
    wages = WageRate.query.order_by(WageRate.effective_date.desc()).limit(10).all() if hasattr(WageRate, "effective_date") else WageRate.query.limit(10).all()

    settings = {
        "DAILY_TOLERANCE_MINUTES": GlobalSettings.daily_tolerance_minutes(),
        "REPORT_BURDEN_PERCENT": GlobalSettings.report_burden_percent(),
        "ALLOWED_EMAIL_DOMAIN": GlobalSettings.allowed_email_domain() or "",
    }

    return render_template(
        "admin/dashboard.html",
        users=users,
        projects=projects,
        wages=wages,
        settings=settings,
    )


@admin_bp.post("/update-settings")
@login_required
@roles_required("admin")
def update_settings():
    # Names should match your dashboard form input names
    tol = request.form.get("DAILY_TOLERANCE_MINUTES", "").strip()
    burden = request.form.get("REPORT_BURDEN_PERCENT", "").strip()
    domain = request.form.get("ALLOWED_EMAIL_DOMAIN", "").strip()

    if tol:
        AppSetting.set("DAILY_TOLERANCE_MINUTES", tol)
    if burden:
        AppSetting.set("REPORT_BURDEN_PERCENT", burden)
    # Domain can be blank to allow any
    AppSetting.set("ALLOWED_EMAIL_DOMAIN", domain)

    flash("Settings updated.", "success")
    return redirect(url_for("admin.dashboard"))


# Optional: keep this stub since earlier logs referenced admin.add_wage
@admin_bp.route("/wages/add", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def add_wage():
    if request.method == "POST":
        try:
            rate = float(request.form.get("rate", "0") or "0")
        except ValueError:
            flash("Invalid rate.", "danger")
            return redirect(url_for("admin.add_wage"))
        eff = request.form.get("effective_date")
        wage = WageRate(rate=rate, effective_date=eff) if eff else WageRate(rate=rate)
        db.session.add(wage)
        db.session.commit()
        flash("Wage rate added.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/add_wage.html")
