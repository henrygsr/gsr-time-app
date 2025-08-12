from datetime import datetime
from ..extensions import db

class ChangeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(120), nullable=False)
    record_id = db.Column(db.String(120), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # created, updated, deleted, unsubmitted, etc.
    changed_by = db.Column(db.Integer, nullable=True)  # user id
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text, default="")
