from datetime import datetime
from flask import Blueprint, render_template, request, send_file
from flask_login import login_required, current_user
from ..extensions import db
from ..models.timeentry import TimeEntry
from ..models.user import User
from ..models.project import Project
from ..utils.pdf import render_pdf_from_template
from ..utils.costing import get_cost_for_entry
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

    # PM restriction: only their projects (or company tasks)
    if current_user.is_project_manager and not current_user.is_admin and not current_user.is_accounting:
        pids = [r[0] for r in db.session.execute(db.text(
            "SELECT project_id FROM p_m_project WHERE pm_user_id=:uid"), {"uid": current_user.id}).all()]
        if pids:
            q = q.filter((TimeEntry.project_id.in_(pids)) | (TimeEntry.project_id==None))
        else:
            q = q.filter(TimeEntry.id==None)

    entries = q.order_by(TimeEntry.work_date.asc()).all()
    can_view_cost = current_user.is_admin or current_user.is_accounting

    rows = []
    sum_hours = 0.0
    sum_labor_cost = 0.0
    sum_total_cost = 0.0
    for e in entries:
        cost = get_cost_for_entry(e)
        rows.append((e, cost))
        sum_hours += (e.hours or 0.0)
        if can_view_cost:
            sum_labor_cost += cost["labor_cost"]
            sum_total_cost += cost["total_cost"]

    return render_template('reports/results.html',
                           rows=rows, start=start, end=end,
                           can_view_cost=can_view_cost,
                           sum_hours=round(sum_hours, 2),
                           sum_labor_cost=round(sum_labor_cost, 2),
                           sum_total_cost=round(sum_total_cost, 2))

@reports_bp.route('/export.csv')
@login_required
def export_csv():
    start = datetime.strptime(request.args.get('start'), "%Y-%m-%d").date()
    end = datetime.strptime(request.args.get('end'), "%Y-%m-%d").date()
    include_archived = request.args.get('include_archived') == '1'
    user_id = request.args.get('user_id') or None
    project_id = request.args.get('project_id') or None
    q = _query_filtered(start, end, include_archived, user_id, project_id)

    # PM restriction
    if current_user.is_project_manager and not current_user.is_admin and not current_user.is_accounting:
        pids = [r[0] for r in db.session.execute(db.text(
            "SELECT project_id FROM p_m_project WHERE pm_user_id=:uid"), {"uid": current_user.id}).all()]
        if pids:
            q = q.filter((TimeEntry.project_id.in_(pids)) | (TimeEntry.project_id==None))
        else:
            q = q.filter(TimeEntry.id==None)

    entries = q.order_by(TimeEntry.work_date.asc()).all()
    can_view_cost = current_user.is_admin or current_user.is_accounting

    output = io.StringIO()
    w = csv.writer(output)
    if can_view_cost:
        w.writerow(["Date","Employee","Project","Hours","Rate","Burden %","Labor Cost","Total Cost","Submitted"])
    else:
        w.writerow(["Date","Employee","Project","Hours","Submitted"])
    for e in entries:
        proj = (e.project.name if e.project else "Company Task")
        if can_view_cost:
            c = get_cost_for_entry(e)
            w.writerow([e.work_date.isoformat(), e.user.username, proj,
                        f"{e.hours:.2f}", f"{c['rate']:.2f}", f"{c['burden_percent']:.2f}",
                        f"{c['labor_cost']:.2f}", f"{c['total_cost']:.2f}",
                        "Yes" if e.is_submitted else "No"])
        else:
            w.writerow([e.work_date.isoformat(), e.user.username, proj,
                        f"{e.hours:.2f}", "Yes" if e.is_submitted else "No"])

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

    # PM restriction
    if current_user.is_project_manager and not current_user.is_admin and not current_user.is_accounting:
        pids = [r[0] for r in db.session.execute(db.text(
            "SELECT project_id FROM p_m_project WHERE pm_user_id=:uid"), {"uid": current_user.id}).all()]
        if pids:
            q = q.filter((TimeEntry.project_id.in_(pids)) | (TimeEntry.project_id==None))
        else:
            q = q.filter(TimeEntry.id==None)

    entries = q.order_by(TimeEntry.work_date.asc()).all()
    can_view_cost = current_user.is_admin or current_user.is_accounting

    rows = []
    sum_hours = 0.0
    sum_labor_cost = 0.0
    sum_total_cost = 0.0
    for e in entries:
        c = get_cost_for_entry(e)
        rows.append((e, c))
        sum_hours += (e.hours or 0.0)
        if can_view_cost:
            sum_labor_cost += c["labor_cost"]
            sum_total_cost += c["total_cost"]

    pdf = render_pdf_from_template('reports/pdf.html',
                                   rows=rows, start=start, end=end,
                                   can_view_cost=can_view_cost,
                                   sum_hours=round(sum_hours, 2),
                                   sum_labor_cost=round(sum_labor_cost, 2),
                                   sum_total_cost=round(sum_total_cost, 2))
    mem = io.BytesIO(pdf)
    mem.seek(0)
    return send_file(mem, mimetype='application/pdf', as_attachment=True, download_name='report.pdf')
