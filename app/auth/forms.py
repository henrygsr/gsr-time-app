# app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=255)],
    )
    submit = SubmitField("Sign In")

class RegisterForm(FlaskForm):
    first_name = StringField("First name", validators=[DataRequired(), Length(max=100)])
    last_name = StringField("Last name", validators=[DataRequired(), Length(max=100)])
    email = StringField(
        "Work email",
        validators=[DataRequired(), Email(), Length(max=255)],
    )
    submit = SubmitField("Create Account")

# Compatibility alias so imports like `from .forms import RegistrationForm`
# keep working even if routes expect `RegistrationForm`.
RegistrationForm = RegisterForm
