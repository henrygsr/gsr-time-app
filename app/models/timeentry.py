from datetime import datetime
from ..extensions import db

class TimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=True)  # company-level tasks may be null
    work_date = db.Column(db.Date, nullable=False, index=True)
    hours = db.Column(db.Float, default=0.0)
    notes = db.Column(db.String(1000), default="")
    is_submitted = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Cost snapshot (set at submit time so wages/burden changes don't affect history)
    hourly_rate_applied = db.Column(db.Float, nullable=True)
    burden_percent_applied = db.Column(db.Float, nullable=True)
    labor_cost = db.Column(db.Float, nullable=True)      # hours * hourly_rate_applied
    total_cost = db.Column(db.Float, nullable=True)      # labor_cost * (1 + burden_percent_applied/100)
