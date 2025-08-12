from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..extensions import db
from ..models.project import Project
from ..models.timeentry import TimeEntry
from ..utils.security import roles_required
from ..utils.changes import log_change

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/')
@login_required
@roles_required('admin')
def index():
    active = Project.query.filter_by(is_archived=False).order_by(Project.name.asc()).all()
    archived = Project.query.filter_by(is_archived=True).order_by(Project.name.asc()).all()
    return render_template('projects/index.html', active=active, archived=archived)

@projects_bp.route('/create', methods=['POST'])
@login_required
@roles_required('admin')
def create():
    name = request.form.get('name', '').strip()
    if not name:
        flash("Project name required.", "danger")
        return redirect(url_for('projects.index'))
    if Project.query.filter_by(name=name).first():
        flash("Project name already exists.", "danger")
        return redirect(url_for('projects.index'))
    p = Project(name=name)
    db.session.add(p)
    log_change("project", "new", "created", {"name": name})
    db.session.commit()
    flash("Project created.", "success")
    return redirect(url_for('projects.index'))

@projects_bp.route('/<int:pid>/archive', methods=['POST'])
@login_required
@roles_required('admin')
def archive(pid):
    p = Project.query.get_or_404(pid)
    p.is_archived = True
    log_change("project", pid, "archived")
    db.session.commit()
    flash("Project archived.", "success")
    return redirect(url_for('projects.index'))

@projects_bp.route('/<int:pid>/unarchive', methods=['POST'])
@login_required
@roles_required('admin')
def unarchive(pid):
    p = Project.query.get_or_404(pid)
    p.is_archived = False
    log_change("project", pid, "unarchived")
    db.session.commit()
    flash("Project unarchived.", "success")
    return redirect(url_for('projects.index'))

@projects_bp.route('/<int:pid>/delete', methods=['POST'])
@login_required
@roles_required('admin')
def delete(pid):
    p = Project.query.get_or_404(pid)
    if TimeEntry.query.filter_by(project_id=pid).first():
        flash("Cannot delete project with time entries.", "danger")
        return redirect(url_for('projects.index'))
    db.session.delete(p)
    log_change("project", pid, "deleted")
    db.session.commit()
    flash("Project deleted.", "success")
    return redirect(url_for('projects.index'))
