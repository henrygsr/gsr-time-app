from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from ..models.user import User
from .forms import RegisterForm, LoginForm
from ..utils.changes import log_change

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        allowed = current_app.config.get("ALLOWED_EMAIL_DOMAIN", "gsrconstruct.com")
        if not form.email.data.endswith(f"@{allowed}"):
            flash(f"Must use @{allowed} email to register.", "danger")
            return render_template('auth/register.html', form=form)
        if User.query.filter((User.email==form.email.data)|(User.username==form.username.data)).first():
            flash("Email or username already taken.", "danger")
            return render_template('auth/register.html', form=form)
        u = User(email=form.email.data, username=form.username.data,
                 password_hash=generate_password_hash(form.password.data))
        db.session.add(u)
        log_change("user", "new", "created", {"email": u.email, "username": u.username})
        db.session.commit()
        flash("Account created. Please sign in.", "success")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if u and check_password_hash(u.password_hash, form.password.data) and not u.is_archived:
            login_user(u, remember=form.remember.data)
            return redirect(url_for('main.dashboard'))
        flash("Invalid credentials or archived account.", "danger")
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
