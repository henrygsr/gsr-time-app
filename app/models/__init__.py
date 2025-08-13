# app/models/__init__.py

# Re-export the SQLAlchemy instance so callers can do `from app.models import db`
from ..extensions import db

# Import and re-export your model classes
# (Make sure these module names match your files under app/models/)
from .user import User
from .project import Project
from .wage_rate import WageRate
from .project_assignment import ProjectAssignment
from .change_log import ChangeLog

__all__ = [
    "db",
    "User",
    "Project",
    "WageRate",
    "ProjectAssignment",
    "ChangeLog",
]
