from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from flask_login import login_required, current_user
from ..extensions import db
from ..models.timeentry import TimeEntry
from ..models.project import Project
from ..utils.csv_utils import parse_patrot_csv
from ..utils.pdf import render_pdf_from_template
from ..utils.changes import log_change
import io, csv

timesheets_bp = Blueprint('timesheets', __name__)

@timesheets_bp.route('/')
@login_required
def index():
    # Show last 14 days by default
    end = date.today()
    start = end - timedelta(days=13)
    entries = (TimeEntry.query
               .filter(TimeEntry.user_id==current_user.id, TimeEntry.work_date.between(start, end))
               .order_by(TimeEntry.work_date.asc())
               .all())
    projects = Project.query.filter_by(is_archived=False).order_by(Project.name.asc()).all()
    return render_template('timesheets/index.html', entries=entries, projects=projects, start=start, end=end)

@timesheets_bp.route('/save', methods=['POST'])
@login_required
def save():
    # Autosave endpoint for a single row
    work_date = request.form.get('work_date')
    project_id = request.form.get('project_id') or None
    hours = float(request.form.get('hours') or 0)
    notes = request.form.get('notes','')
    d = datetime.strptime(work_date, "%Y-%m-%d").date()
    entry = (TimeEntry.query.filter_by(user_id=current_user.id, work_date=d, project_id=project_id).first()
             if project_id else None)
    if not entry:
        entry = TimeEntry(user_id=current_user.id, work_date=d, project_id=project_id)
        db.session.add(entry)
    if entry.is_submitted:
        return jsonify({"ok": False, "message": "Entry is locked."}), 400
    entry.hours = hours
    entry.notes = notes
    log_change("timeentry", entry.id or "new", "autosave", {"date": work_date, "hours": hours})
    db.session.commit()
    return jsonify({"ok": True})

@timesheets_bp.route('/import', methods=['GET','POST'])
@login_required
def import_csv():
    if request.method == 'POST':
        f = request.files.get('file')
        if not f:
            flash("No file uploaded.", "danger")
            return redirect(url_for('timesheets.import_csv'))
        totals = parse_patrot_csv(f)
        # Store in session-like cache? For simplicity we reuse in client by recalculating on submit; here just echo
        return render_template('timesheets/import_result.html', totals=totals)
    return render_template('timesheets/import.html')

def _daily_total_for_user(d):
    # Sum of all projects for user/date (including None project)
    q = db.session.query(db.func.coalesce(db.func.sum(TimeEntry.hours), 0.0)).filter(
        TimeEntry.user_id==current_user.id, TimeEntry.work_date==d)
    return float(q.scalar() or 0.0)

@timesheets_bp.route('/submit', methods=['POST'])
@login_required
def submit():
    # Submit a range of days; validate Patriot totals if provided
    start = datetime.strptime(request.form.get('start'), "%Y-%m-%d").date()
    end = datetime.strptime(request.form.get('end'), "%Y-%m-%d").date()
    # Patriot totals passed as JSON-like "YYYY-MM-DD:hours,..." (simple for demo)
    raw = request.form.get('patriot_totals', '').strip()
    patriot = {}
    if raw:
        for kv in raw.split(','):
            if ':' in kv:
                k,v = kv.split(':',1)
                try:
                    patriot[datetime.strptime(k.strip(), "%Y-%m-%d").date()] = float(v.strip())
                except Exception:
                    pass
    tol_minutes = float(current_app.config.get("DAILY_TOLERANCE_MINUTES", 6))
    tol_hours = tol_minutes/60.0

    # Validate each day if provided
    for n in range((end-start).days+1):
        d = start + timedelta(days=n)
        if d in patriot:
            tot = _daily_total_for_user(d)
            if abs(tot - patriot[d]) > tol_hours:
                flash(f"Day {d} mismatch: Patriot {patriot[d]:.2f}h vs Entered {tot:.2f}h (tolerance {tol_hours:.2f}h). Fix before submitting.", "danger")
                return redirect(url_for('timesheets.index'))

    # Lock
    changed = 0
    entries = (TimeEntry.query.filter(TimeEntry.user_id==current_user.id, TimeEntry.work_date.between(start, end)).all())
    for e in entries:
        if not e.is_submitted:
            e.is_submitted = True
            e.submitted_at = datetime.utcnow()
            changed += 1
            log_change("timeentry", e.id, "submitted", {"date": str(e.work_date), "hours": e.hours})
    db.session.commit()
    flash(f"Submitted {changed} entries.", "success")
    return redirect(url_for('timesheets.index'))

@timesheets_bp.route('/export.csv')
@login_required
def export_csv():
    # Export user's entries in range
    start = request.args.get('start')
    end = request.args.get('end')
    start = datetime.strptime(start, "%Y-%m-%d").date() if start else (date.today() - timedelta(days=13))
    end = datetime.strptime(end, "%Y-%m-%d").date() if end else date.today()

    entries = (TimeEntry.query
               .filter(TimeEntry.user_id==current_user.id, TimeEntry.work_date.between(start, end))
               .order_by(TimeEntry.work_date.asc())
               .all())
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["Date","Project","Hours","Notes","Submitted"])
    for e in entries:
        w.writerow([e.work_date.isoformat(), (e.project.name if e.project else "Company Task"), f"{e.hours:.2f}", e.notes, "Yes" if e.is_submitted else "No"])
    mem = io.BytesIO(output.getvalue().encode('utf-8'))
    mem.seek(0)
    return send_file(mem, mimetype='text/csv', as_attachment=True, download_name='my_time.csv')

@timesheets_bp.route('/export.pdf')
@login_required
def export_pdf():
    start = request.args.get('start')
    end = request.args.get('end')
    start = datetime.strptime(start, "%Y-%m-%d").date() if start else (date.today() - timedelta(days=13))
    end = datetime.strptime(end, "%Y-%m-%d").date() if end else date.today()
    entries = (TimeEntry.query
               .filter(TimeEntry.user_id==current_user.id, TimeEntry.work_date.between(start, end))
               .order_by(TimeEntry.work_date.asc())
               .all())
    pdf = render_pdf_from_template('timesheets/pdf.html', entries=entries, start=start, end=end)
    return send_file(io.BytesIO(pdf), mimetype='application/pdf', as_attachment=True, download_name='my_time.pdf')
