# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf

from .models import db  # SQLAlchemy() instance defined in app/models/__init__.py

migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app() -> Flask:
    app = Flask(__name__)

    # ---- Config ----
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    database_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
    # Normalize old postgres URL format if present
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ---- Extensions ----
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf.init_app(app)

    # Make csrf_token() available in ALL templates (even without a FlaskForm)
    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": generate_csrf}

    # ---- Blueprints ----
    # Import inside factory to avoid circular imports
    from .main.routes import main_bp
    from .auth.routes import auth_bp
    from .projects.routes import projects_bp
    from .timesheets.routes import timesheets_bp
    from .reports.routes import reports_bp
    from .admin import admin_bp  # package defines blueprint and imports routes

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(timesheets_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)

    # ---- User loader ----
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    return app
