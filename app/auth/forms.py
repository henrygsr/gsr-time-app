from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log In")

# If you don't use registration, you can delete this class
# and also remove it from any imports/routes.
class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create Account")
