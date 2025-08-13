# app/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

# Single global db instance for the whole app
db = SQLAlchemy()

# ---- OPTIONAL RE-EXPORTS ----------------------------------------------------
# If your models are split across files like app/models/user.py, project.py, etc.,
# these imports will re-export them at app.models.* for convenience.
# If a given file doesn't exist yet, the try/except prevents startup crashes.
try:  # adjust names to match your repo layout
    from .user import User  # noqa: F401
except Exception:
    pass
try:
    from .project import Project  # noqa: F401
except Exception:
    pass
try:
    from .wage import WageRate  # noqa: F401
except Exception:
    pass
try:
    from .project_assignment import ProjectAssignment  # noqa: F401
except Exception:
    pass
try:
    from .timesheet import TimesheetEntry  # noqa: F401
except Exception:
    pass
try:
    from .change_log import ChangeLog  # noqa: F401
except Exception:
    pass
# -----------------------------------------------------------------------------
