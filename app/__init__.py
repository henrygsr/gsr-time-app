# app/__init__.py
import os
from flask import Flask
from flask_login import LoginManager
from .models import db

# Try to import your blueprints; if some don't exist, skip them gracefully.
def _try_import_blueprint(path, attr):
    try:
        mod = __import__(path, fromlist=[attr])
        return getattr(mod, attr)
    except Exception:
        return None

login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # ---- Config ----
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ---- Extensions ----
    db.init_app(app)
    login_manager.init_app(app)

    # If you have an auth blueprint providing /login, set it as the login view.
    # Otherwise Flask-Login will redirect to /login by default if you create such a route.
    login_manager.login_view = "auth.login"

    # ---- Blueprints (register if present) ----
    blueprints = [
        ("app.main", "main_bp", None),                   # /
        ("app.timesheets", "timesheets_bp", "/timesheets"),
        ("app.projects", "projects_bp", "/projects"),
        ("app.reports", "reports_bp", "/reports"),
        ("app.admin", "admin_bp", "/admin"),
        ("app.auth", "auth_bp", "/"),                    # optional auth package
    ]
    for module_path, bp_name, prefix in blueprints:
        bp = _try_import_blueprint(module_path, bp_name)
        if bp:
            app.register_blueprint(bp, url_prefix=prefix)

    # ---- User loader for Flask-Login (adjust to your User model) ----
    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            from .models import User  # imported here to avoid circular imports
            return User.query.get(int(user_id))
        except Exception:
            return None

    # ---- Health route (optional) ----
    @app.get("/healthz")
    def healthcheck():
        return {"status": "ok"}, 200

    return app
