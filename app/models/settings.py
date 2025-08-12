from ..extensions import db

class GlobalSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    burden_percent = db.Column(db.Float, default=30.0)

def ensure_global_settings():
    if not GlobalSettings.query.first():
        db.session.add(GlobalSettings(burden_percent=30.0))
        db.session.commit()
