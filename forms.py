from flask_wtf import Form 
from wtforms import StringField, PasswordField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

from models import User

def name_exists(form, field):
    if User.query.filter_by(display_name=field.data).first() != None:
        raise ValidationError('User with that Display Name already exists')

def email_exists(form, field):
    if User.query.filter_by(email=field.data).first() != None:
        raise ValidationError('User with that Email already exists')

class RegisterForm(Form):

    display_name = StringField(
        'Display Name',
        validators=[
            DataRequired(),
            Regexp(
                r'^^[A-Za-z0-9 _]*[A-Za-z0-9][A-Za-z0-9 _]*$',
                message=("Display Name should be one word, letters, "
                         "numbers, spaces, and underscores only.")
            ),
            name_exists
        ])

    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])

    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )