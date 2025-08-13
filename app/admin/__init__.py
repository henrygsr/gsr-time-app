# app/admin/__init__.py
from flask import Blueprint

admin_bp = Blueprint("admin", __name__, template_folder="templates", static_folder="static")

# Import routes AFTER creating the blueprint to avoid circular imports
from . import routes  # noqa: E402,F401
