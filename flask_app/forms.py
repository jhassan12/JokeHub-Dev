from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
)

from .models import User

def trim(data):
    return data.strip() if data else ""

class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=3, max=50)], filters=[trim]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=50)], filters=[trim])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")

    def validate_password(self, password):
        error_msg = 'Password must contain an uppercase letter.\nPassword must contain a lowercase letter.\nPassword must contain a number from 0-9.\nPassword must contain a special character (including # @ $ &).\nThe password must not contain a space.'

        special_chars = '#@$&'

        has_capital_letter = False
        has_lower_letter = False
        has_digit = False
        has_special_char = False

        for c in password.data:
            if c.isspace():
                raise ValidationError(error_msg)

            if c.isalpha() and c.isupper():
                has_capital_letter = True

            if c.isalpha() and c.islower():
                has_lower_letter = True

            if c.isdigit():
                has_digit = True

            if c in special_chars:
                has_special_char = True

        if not has_capital_letter or not has_lower_letter or not has_digit or not has_special_char:
            raise ValidationError(error_msg)

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class JokeForm(FlaskForm):
    content = TextAreaField(
        "Enter joke", validators=[InputRequired(), Length(min=3, max=500)], filters=[trim]
    )

    submit = SubmitField("Create Joke")

class JokeCommentForm(FlaskForm):
    content = TextAreaField(
        "Enter comment", validators=[InputRequired(), Length(min=3, max=500)], filters=[trim]
    )

    submit = SubmitField("Submit comment")

class ChangeUsernameForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=50)], filters=[trim])

    def validate_username(self, username):
        user = User.objects(username=username.data).first()

        if user is not None:
            raise ValidationError("Username is taken.")

    submit = SubmitField("Change Username")

class SearchForm(FlaskForm):
    query = StringField(validators=[InputRequired(), Length(min=1)], filters=[trim])

    submit = SubmitField("Search")

