from flask import Blueprint

# Blueprint for all admin views
admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",   # app/admin/templates
    static_folder=None,
)

# Import routes after blueprint created so decorators can bind correctly
from . import routes  # noqa: E402,F401
