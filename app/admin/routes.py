from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..utils.security import admin_required
from ..extensions import db
from ..models.settings import AppSetting, GlobalSettings

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
    static_folder=None,
)


@admin_bp.get("/")
@login_required
@admin_required
def dashboard():
    app_settings = AppSetting.query.first()
    global_settings = GlobalSettings.query.first()
    return render_template(
        "admin/dashboard.html",
        app_settings=app_settings,
        global_settings=global_settings,
    )


@admin_bp.post("/update-settings")
@login_required
@admin_required
def update_settings():
    # App-level OT/DT settings
    s = AppSetting.query.first()
    if not s:
        s = AppSetting()
        db.session.add(s)

    s.overtime_threshold_hours_per_day = int(
        request.form.get("overtime_threshold_hours_per_day", 8)
    )
    s.overtime_multiplier = float(request.form.get("overtime_multiplier", 1.5))
    s.doubletime_threshold_hours_per_day = int(
        request.form.get("doubletime_threshold_hours_per_day", 12)
    )
    s.doubletime_multiplier = float(request.form.get("doubletime_multiplier", 2.0))

    # Burden percent (kept on GlobalSettings for compatibility with costing.py)
    gs = GlobalSettings.query.first()
    if not gs:
        gs = GlobalSettings()
        db.session.add(gs)
    gs.burden_percent = float(request.form.get("burden_percent", 0))

    db.session.commit()
    flash("Settings updated.", "success")
    return redirect(url_for("admin.dashboard"))
