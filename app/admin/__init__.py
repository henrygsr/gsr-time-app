from flask import Blueprint

# Single source of truth for the admin blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Import routes so their @admin_bp.route decorators run
from . import routes  # noqa: E402,F401
