import os
from flask import Flask, redirect, url_for
from .extensions import db, migrate, login_manager, csrf
from .models.settings import AppSetting, GlobalSettings


def create_app() -> Flask:
    app = Flask(__name__)

    # Basic config
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Database (Render sets DATABASE_URL). Make it SQLAlchemy 2.x friendly.
    db_uri = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")
    # Render/Heroku style fix
    if db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql+psycopg://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Blueprints
    from .auth.routes import auth_bp
    from .projects.routes import projects_bp
    from .timesheets.routes import timesheets_bp
    from .admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(timesheets_bp)
    app.register_blueprint(admin_bp)

    # Default route -> login
    @app.route("/")
    def root():
        return redirect(url_for("auth.login"))

    # Ensure schema + seed default settings on startup
    with app.app_context():
        db.create_all()
        _ensure_default_settings()

    return app


def _ensure_default_settings() -> None:
    """Create initial settings rows if they don't exist yet."""
    # Global settings (used by costing for burden percent)
    gs = GlobalSettings.query.first()
    if not gs:
        gs = GlobalSettings(burden_percent=0.0)
        db.session.add(gs)

    # App settings (used by Admin page & overtime logic)
    s = AppSetting.query.first()
    if not s:
        s = AppSetting(
            overtime_threshold_hours_per_day=8,
            overtime_multiplier=1.5,
            doubletime_threshold_hours_per_day=12,
            doubletime_multiplier=2.0,
        )
        db.session.add(s)

    db.session.commit()
