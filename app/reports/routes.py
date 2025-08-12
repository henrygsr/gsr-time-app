from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, send_file, abort
from flask_login import login_required, current_user
from ..utils.security import roles_required
from ..extensions import db
from ..models.timeentry import TimeEntry
from ..models.user import User
from ..models.project import Project
from ..models.settings import GlobalSettings
from ..utils.pdf import render_pdf_from_template
import io, csv

reports_bp = Blueprint('reports', __name__)

def _query_filtered(start, end, include_archived, user_id=None, project_id=None):
    q = TimeEntry.query.join(User, TimeEntry.user_id==User.id).join(Project, isouter=True)
    if user_id:
        q = q.filter(TimeEntry.user_id==user_id)
    if project_id:
        q = q.filter(TimeEntry.project_id==project_id)
    q = q.filter(TimeEntry.work_date.between(start, end))
    if not include_archived:
        q = q.filter((User.is_archived==False) & ((Project.is_archived==False) | (TimeEntry.project_id==None)))
    return q

@reports_bp.route('/')
@login_required
def index():
    # Accounting can view; PMs see only their projects; Admins all
    users = []
    projects = []
    if current_user.is_admin or current_user.is_accounting:
        users = User.query.order_by(User.username.asc()).all()
        projects = Project.query.order_by(Project.name.asc()).all()
    return render_template('reports/index.html', users=users, projects=projects)

@reports_bp.route('/results')
@login_required
def results():
    start = datetime.strptime(request.args.get('start'), "%Y-%m-%d").date()
    end = datetime.strptime(request.args.get('end'), "%Y-%m-%d").date()
    include_archived = request.args.get('include_archived') == '1'
    user_id = request.args.get('user_id') or None
    project_id = request.args.get('project_id') or None

    q = _query_filtered(start, end, include_archived, user_id, project_id)
    # PM restriction: only their projects
    if current_user.is_project_manager and not current_user.is_admin and not current_user.is_accounting:
        # Load their project ids via raw SQL for brevity
        pids = [r[0] for r in db.session.execute(db.text("SELECT project_id FROM p_m_project WHERE pm_user_id=:uid"), {"uid": current_user.id}).all()]
        if pids:
            q = q.filter((TimeEntry.project_id.in_(pids)) | (TimeEntry.project_id==None))
        else:
            q = q.filter(TimeEntry.id==None)

    entries = q.order_by(TimeEntry.work_date.asc()).all()
    return render_template('reports/results.html', entries=entries, start=start, end=end)

@reports_bp.route('/export.csv')
@login_required
def export_csv():
    start = datetime.strptime(request.args.get('start'), "%Y-%m-%d").date()
    end = datetime.strptime(request.args.get('end'), "%Y-%m-%d").date()
    include_archived = request.args.get('include_archived') == '1'
    user_id = request.args.get('user_id') or None
    project_id = request.args.get('project_id') or None
    q = _query_filtered(start, end, include_archived, user_id, project_id)

    entries = q.order_by(TimeEntry.work_date.asc()).all()
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["Date","Employee","Project","Hours","Submitted"])
    for e in entries:
        w.writerow([e.work_date.isoformat(), e.user.username, (e.project.name if e.project else "Company Task"), f"{e.hours:.2f}", "Yes" if e.is_submitted else "No"])
    mem = io.BytesIO(output.getvalue().encode('utf-8'))
    mem.seek(0)
    return send_file(mem, mimetype='text/csv', as_attachment=True, download_name='report.csv')

@reports_bp.route('/export.pdf')
@login_required
def export_pdf():
    start = datetime.strptime(request.args.get('start'), "%Y-%m-%d").date()
    end = datetime.strptime(request.args.get('end'), "%Y-%m-%d").date()
    include_archived = request.args.get('include_archived') == '1'
    user_id = request.args.get('user_id') or None
    project_id = request.args.get('project_id') or None
    q = _query_filtered(start, end, include_archived, user_id, project_id)
    entries = q.order_by(TimeEntry.work_date.asc()).all()
    pdf = render_pdf_from_template('reports/pdf.html', entries=entries, start=start, end=end)
    return send_file(io.BytesIO(pdf), mimetype='application/pdf', as_attachment=True, download_name='report.pdf')
