from datetime import datetime, date
from ..extensions import db

class WageRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    effective_date = db.Column(db.Date, nullable=False, index=True)
    hourly_rate = db.Column(db.Float, nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'effective_date', name='uq_user_effective'),)
