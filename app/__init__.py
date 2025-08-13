# app/__init__.py
import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf

from .models import db  # relies on app/models/__init__.py exporting db


login_manager = LoginManager()
login_manager.login_view = "auth.login"

csrf = CSRFProtect()
migrate = Migrate()


def create_app() -> Flask:
    app = Flask(__name__)

    # ---- Config ----
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Prefer DATABASE_URL if set (Render Postgres), else fall back to SQLite.
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        # SQLAlchemy 2.x expects postgresql+psycopg for psycopg3
        db_url = db_url.replace("postgres://", "postgresql+psycopg://")
    else:
        db_url = "sqlite:///app.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ---- Extensions ----
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Make csrf_token() available in Jinja (fixes “csrf_token is undefined”)
    app.jinja_env.globals["csrf_token"] = generate_csrf

    # ---- Blueprints ----
    from .auth.routes import auth_bp
    from .timesheets.routes import timesheets_bp
    from .projects.routes import projects_bp
    from .admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(timesheets_bp, url_prefix="/timesheets")
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # ---- DB bootstrap (create tables + defaults on first run) ----
    with app.app_context():
        # Ensure all tables exist (covers fresh SQLite or empty Postgres)
        db.create_all()

        _ensure_default_settings()
        _seed_admin_user_if_env_present()

    return app


@login_manager.user_loader
def load_user(user_id):
    from .models import User  # imported here to avoid circulars
    return User.query.get(int(user_id))


def _ensure_default_settings():
    """Create an AppSetting row if none exists yet."""
    try:
        from .models import AppSetting
    except Exception:
        # If the model isn't present, skip silently.
        return

    if AppSetting.query.first() is None:
        s = AppSetting(
            overtime_threshold_hours_per_day=8,
            overtime_multiplier=1.5,
            doubletime_threshold_hours_per_day=12,
            doubletime_multiplier=2.0,
        )
        db.session.add(s)
        db.session.commit()


def _seed_admin_user_if_env_present():
    """
    Seed an initial admin if ADMIN_EMAIL and ADMIN_PASSWORD are provided
    via environment variables. Safe to run repeatedly.
    """
    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        return

    from .models import User

    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        # Make sure they have admin flags
        if not existing.is_admin:
            existing.is_admin = True
            db.session.commit()
        return

    # Create the admin user
    user = User(
        email=admin_email,
        username=(admin_email.split("@")[0])[:80],
        is_admin=True,
        is_project_manager=True,
        is_accounting=True,
    )
    user.set_password(admin_password)
    db.session.add(user)
    db.session.commit()
