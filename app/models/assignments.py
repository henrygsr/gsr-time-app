from ..extensions import db

# PM-to-Project assignment mapping
class PMProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pm_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False, index=True)
    __table_args__ = (db.UniqueConstraint('pm_user_id', 'project_id', name='uq_pm_project'),)
