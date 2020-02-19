from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

from models import User


def name_exists(form, display_name):
    """Raise an error if a display name has already been taken."""

    if User.query.filter_by(display_name=display_name).first() != None:
        raise ValidationError('User with that Display Name already exists')


def email_exists(form, email):
    """Raise an error if a email has already been taken."""

    if User.query.filter_by(email=email).first() != None:
        raise ValidationError('User with that Email already exists')


class CreateMessageForm(FlaskForm):

    subject = StringField('Subject')
    contents = StringField('Contents', [validators.DataRequired(),
                                        validators.Length(min=2, max=1000,
                                                          message='Messages must be between 2 and 1000 characters.')])


class CreatePostForm(FlaskForm):

    post_text = StringField('Post text', [validators.DataRequired(),
                                          validators.Length(min=2, max=1000,
                                                            message='Messages must be between 2 and 1000 characters.')])


class LoginForm(FlaskForm):

    email = StringField(
        'Email',
        validators=[
            DataRequired("Please enter a valid email address."),
            Email(),
            email_exists
        ])

    password = PasswordField(
        'Password',
        validators=[
            DataRequired("Please enter a password."),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])


class RegisterForm(FlaskForm):

    display_name = StringField(
        'Display Name',
        validators=[
            DataRequired(
                "Please enter the name you'd like to be called on BrightBook."),
            Regexp(
                r'^^[A-Za-z0-9 _]*[A-Za-z0-9][A-Za-z0-9 _]*$',
                message=("Display Name should be made of letters, "
                         "numbers, spaces, and underscores only.")
            ),
            name_exists
        ])

    email = StringField(
        'Email',
        validators=[
            DataRequired("Please enter a valid email address."),
            Email(),
            email_exists
        ])

    password = PasswordField(
        'Password',
        validators=[
            DataRequired("Please enter a password."),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])

    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired("Please confirm your password.")]

    )
