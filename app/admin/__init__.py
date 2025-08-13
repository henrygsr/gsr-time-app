# app/admin/__init__.py
from flask import Blueprint

# All admin routes live under /admin
admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",  # app/admin/templates/...
    static_folder=None,
)

# Import routes after the blueprint is created to avoid circular imports
from . import routes  # noqa: E402,F401
