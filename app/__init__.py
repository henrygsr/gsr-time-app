import os
from flask import Flask, render_template
from .config import Config
from .extensions import db, migrate, login_manager, csrf
from .models import user, project, timeentry, wage, settings, changelog, assignments
from .auth.routes import auth_bp
from .main.routes import main_bp
from .projects.routes import projects_bp
from .timesheets.routes import timesheets_bp
from .reports.routes import reports_bp
from .admin.routes import admin_bp


def _bootstrap_roles():
    """
    Ensure there is at least one admin.
    Optionally promote users based on env vars:
      BOOTSTRAP_ADMIN_EMAILS=alice@gsrconstruct.com,bob@gsrconstruct.com
      BOOTSTRAP_ACCOUNTING_EMAILS=carol@gsrconstruct.com
    """
    from .models.user import User  # local import to avoid circulars

    changed = False

    # Promote by env vars (if set)
    admins_env = os.environ.get("BOOTSTRAP_ADMIN_EMAILS", "")
    acct_env = os.environ.get("BOOTSTRAP_ACCOUNTING_EMAILS", "")
    admin_emails = [e.strip().lower() for e in admins_env.split(",") if e.strip()]
    acct_emails = [e.strip().lower() for e in acct_env.split(",") if e.strip()]

    if admin_emails or acct_emails:
        for u in User.query.all():
            em = (u.email or "").lower()
            if em in admin_emails and not u.is_admin:
                u.is_admin = True
                changed = True
            if em in acct_emails and not u.is_accounting:
                u.is_accounting = True
                changed = True

    # Ensure at least one admin exists; if none, promote the earliest user
    if User.query.count() > 0 and User.query.filter_by(is_admin=True).count() == 0:
        first_user = User.query.order_by(User.id.asc()).first()
        first_user.is_admin = True
        changed = True

    if changed:
        db.session.commit()


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

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("errors/403.html"), 403

    with app.app_context():
        db.create_all()
        settings.ensure_global_settings()
        _bootstrap_roles()

    return app


# also allow 'gunicorn app:app'
app = create_app()
