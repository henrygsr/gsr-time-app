from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager, csrf
from .models import user, project, timeentry, wage, settings, changelog, assignments
from .auth.routes import auth_bp
from .main.routes import main_bp
from .projects.routes import projects_bp
from .timesheets.routes import timesheets_bp
from .reports.routes import reports_bp
from .admin.routes import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(timesheets_bp, url_prefix="/timesheets")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    with app.app_context():
        db.create_all()
        settings.ensure_global_settings()

    return app

# NEW: allow 'gunicorn app:app' as an entrypoint too
app = create_app()
