from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from ..models import db, User
from .forms import LoginForm, RegistrationForm

auth_bp = Blueprint("auth", __name__, url_prefix="/")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            nxt = request.args.get("next")
            return redirect(nxt or url_for("projects.index"))  # pick your landing page
        flash("Invalid email or password.", "danger")
    return render_template("auth/login.html", form=form)
