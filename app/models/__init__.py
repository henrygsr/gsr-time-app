# app/models/__init__.py
from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

# A single SQLAlchemy instance for the whole app.
# In app/__init__.py you should call: db.init_app(app)
db = SQLAlchemy()

# Re-export your model classes for convenient imports like:
# from app.models import User, Project, WageRate, ProjectAssignment, ChangeLog
try:
    from .user import User  # noqa: F401
except Exception:
    # Leave import optional to avoid circulars during tooling/migrations.
    User = None  # type: ignore[assignment]

try:
    from .project import Project, ProjectAssignment  # noqa: F401
except Exception:
    Project = ProjectAssignment = None  # type: ignore[assignment]

try:
    from .wage import WageRate  # noqa: F401
except Exception:
    WageRate = None  # type: ignore[assignment]

try:
    from .change_log import ChangeLog  # noqa: F401
except Exception:
    ChangeLog = None  # type: ignore[assignment]
