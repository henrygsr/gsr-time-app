from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..extensions import db
from ..utils.security import roles_required
from ..models.user import User
from ..models.timeentry import TimeEntry
from ..models.project import Project
from ..models.wage import WageRate
from ..models.settings import GlobalSettings
from ..models.assignments import PMProject
from ..utils.changes import log_change

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
@roles_required('admin')
def dashboard():
    users = User.query.order_by(User.username.asc()).all()
    settings = GlobalSettings.query.first()
    return render_template('admin/dashboard.html', users=users, settings=settings)

@admin_bp.route('/settings', methods=['POST'])
@login_required
@roles_required('admin')
def update_settings():
    settings = GlobalSettings.query.first()
    settings.burden_percent = float(request.form.get('burden_percent') or 0)
    log_change("settings", settings.id, "updated", {"burden_percent": settings.burden_percent})
    db.session.commit()
    flash("Settings updated.", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users/<int:uid>/archive', methods=['POST'])
@login_required
@roles_required('admin')
def archive_user(uid):
    u = User.query.get_or_404(uid)
    u.is_archived = True
    log_change("user", uid, "archived")
    db.session.commit()
    flash("User archived.", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users/<int:uid>/delete', methods=['POST'])
@login_required
@roles_required('admin')
def delete_user(uid):
    if TimeEntry.query.filter_by(user_id=uid).first():
        flash("Cannot delete user with time entries.", "danger")
        return redirect(url_for('admin.dashboard'))
    u = User.query.get_or_404(uid)
    db.session.delete(u)
    log_change("user", uid, "deleted")
    db.session.commit()
    flash("User deleted.", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users/<int:uid>/roles', methods=['POST'])
@login_required
@roles_required('admin')
def update_roles(uid):
    u = User.query.get_or_404(uid)
    u.is_project_manager = bool(request.form.get('is_project_manager'))
    u.is_accounting = bool(request.form.get('is_accounting'))
    u.is_admin = bool(request.form.get('is_admin'))
    log_change("user", uid, "roles_updated", {"pm": u.is_project_manager, "acct": u.is_accounting, "admin": u.is_admin})
    db.session.commit()
    flash("Roles updated.", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users/<int:uid>/wage', methods=['POST'])
@login_required
@roles_required('admin')
def add_wage(uid):
    eff = datetime.strptime(request.form.get('effective_date'), "%Y-%m-%d").date()
    rate = float(request.form.get('hourly_rate'))
    w = WageRate(user_id=uid, effective_date=eff, hourly_rate=rate)
    db.session.add(w)
    log_change("wage", "new", "created", {"user_id": uid, "effective_date": str(eff), "hourly_rate": rate})
    db.session.commit()
    flash("Wage rate added.", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users/<int:uid>/assign_projects', methods=['POST'])
@login_required
@roles_required('admin')
def assign_projects(uid):
    # expects a list of project ids in form 'project_ids'
    ids = [int(x) for x in request.form.getlist('project_ids')]
    # Clear existing
    PMProject.query.filter_by(pm_user_id=uid).delete()
    for pid in ids:
        db.session.add(PMProject(pm_user_id=uid, project_id=pid))
    log_change("pmproject", uid, "assigned", {"project_ids": ids})
    db.session.commit()
    flash("Project assignments updated.", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/unsubmit/<int:uid>', methods=['POST'])
@login_required
@roles_required('admin')
def unsubmit_latest(uid):
    # Find the most recent submitted date(s) for that user and unlock them
    last = (TimeEntry.query
            .filter_by(user_id=uid, is_submitted=True)
            .order_by(TimeEntry.work_date.desc())
            .first())
    if not last:
        flash("No submitted entries to unsubmit.", "warning")
        return redirect(url_for('admin.dashboard'))
    d = last.work_date
    entries = TimeEntry.query.filter_by(user_id=uid, work_date=d, is_submitted=True).all()
    for e in entries:
        e.is_submitted = False
        e.submitted_at = None
        log_change("timeentry", e.id, "unsubmitted", {"date": str(d)})
    db.session.commit()
    flash(f"Unsubmitted entries for {d}.", "success")
    return redirect(url_for('admin.dashboard'))
