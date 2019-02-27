from flask_wtf import FlaskForm as Form
from models import User
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

def username_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that username already exists.')

def display_name_exists(form, field):
    if User.select().where(User.display_name == field.data).exists():
        raise ValidationError('User with that display name already exists.')

def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')

class RegisterForm(Form):
    username = StringField(
        'Username',
        validators = [
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message = ("Username should be one word, letters, "
                         "numbers, and underscores only.")
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
    # display_name = StringField(
    #     'Display Name',
    #     validators = [
    #         DataRequired(),
    #         display_name_exists
    #     ]
    # )
    password = PasswordField(
        'Password',
        validators = [
            DataRequired(),
            Length(min = 2),
            EqualTo('password2', message = 'Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators = [DataRequired()]
    )

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

class PostForm(Form):
    content = TextAreaField(
        "enter POST here", 
        validators = [
        DataRequired()
        ]
    )
