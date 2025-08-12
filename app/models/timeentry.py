from datetime import datetime, date
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
