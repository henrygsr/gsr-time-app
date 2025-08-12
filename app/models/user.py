from datetime import datetime
from ..extensions import db, login_manager
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_project_manager = db.Column(db.Boolean, default=False)
    is_accounting = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wages = db.relationship("WageRate", backref="user", lazy="dynamic")
    time_entries = db.relationship("TimeEntry", backref="user", lazy="dynamic")

    def active(self):
        return not self.is_archived

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
