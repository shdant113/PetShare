from flask_wtf import FlaskForm as Form
from models import User
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

''' custom validators '''

def username_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that username already exists.')

def display_name_exists(form, field):
    if User.select().where(User.display_name == field.data).exists():
        raise ValidationError('User with that display name already exists.')

def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')

''' registration '''
class RegisterForm(Form):
    username = StringField(
        'Username',
        validators = [
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message = ("Username should be letters, numbers, and underscores only.")
            ),
            username_exists
        ])
    email = StringField(
        'Email',
        validators = [
            DataRequired(),
            Email(),
            email_exists
        ])
    display_name = StringField(
        'Display Name',
        validators = [
            DataRequired(),
            display_name_exists
        ]
    )
    location = StringField(
        'Location',
        validators = [
            DataRequired()
        ]
    )
    password = PasswordField(
        'Password',
        validators = [
            DataRequired(),
            Length(min = 2),
            EqualTo('password2', message = 'Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators = [
            DataRequired()
        ]
    )

''' login '''
class LoginForm(Form):
    email = StringField(
        'Email', 
        validators = [
            DataRequired(), 
            Email()
        ]
    )
    password = PasswordField(
        'Password', 
        validators = [
            DataRequired()
        ]
    )

''' posting '''
class PostForm(Form):
    content = TextAreaField(
        "List all the details!", 
        validators = [
            DataRequired()
        ]
    )
    requested_time = DateTimeField(
        "When do you need a pet sitter?"
        validators = [
            DataRequired()
        ]
    )
