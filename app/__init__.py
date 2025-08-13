import os
from flask import Flask
from .extensions import db, migrate, login_manager

# Configure Flask-Login
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"

def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=False)

    # Core config
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///app.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id: str):
        from .models.user import User
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Register blueprints (import inside to avoid circular imports)
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .timesheets.routes import timesheets_bp
    from .projects.routes import projects_bp
    from .reports.routes import reports_bp
    try:
        # If you added the admin dashboard blueprint
        from .admin import admin_bp  # type: ignore
    except Exception:
        admin_bp = None

    app.register_blueprint(auth_bp)  # /login, /register, /logout
    app.register_blueprint(main_bp)  # /
    app.register_blueprint(timesheets_bp, url_prefix="/timesheets")
    app.register_blueprint(projects_bp,  url_prefix="/projects")
    app.register_blueprint(reports_bp,   url_prefix="/reports")
    if admin_bp:
        app.register_blueprint(admin_bp, url_prefix="/admin")

    # Health check (handy for Render)
    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}, 200

    return app
