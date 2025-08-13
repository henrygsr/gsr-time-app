import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from ..models import db
from ..models.user import User
from .forms import LoginForm, RegistrationForm

auth_bp = Blueprint("auth", __name__)

def _allowed_email(email: str) -> bool:
    """Restrict registrations to an allowed domain if provided."""
    allowed = (os.environ.get("ALLOWED_EMAIL_DOMAIN") or "").strip().lower()
    return not allowed or email.lower().endswith("@" + allowed)

def _is_bootstrap_admin(email: str) -> bool:
    raw = os.environ.get("BOOTSTRAP_ADMIN_EMAILS", "") or ""
    emails = [e.strip().lower() for e in raw.split(",") if e.strip()]
    return email.lower() in emails

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        if not _allowed_email(email):
            flash("Email domain not allowed for self-registration.", "danger")
            return render_template("auth/register.html", form=form)

        if User.query.filter_by(email=email).first():
            flash("That email is already registered.", "warning")
            return redirect(url_for("auth.login"))

        user = User(
            email=email,
            name=form.name.data.strip(),
            role="admin" if _is_bootstrap_admin(email) else "user",
            is_active=True,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
        else:
            login_user(user, remember=form.remember.data)
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.dashboard"))

    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
