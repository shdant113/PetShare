from flask_wtf import FlaskForm as Form
from models import *
from wtforms import SelectField, StringField, PasswordField, TextAreaField, DateTimeField, IntegerField, DateField, SubmitField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

''' custom validators for registration '''

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
        ]
    )
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
    pet = SelectField(
        coerce=int,
        label='Choose from your pets.'
    )
    content = TextAreaField(
        "List all the details!", 
        validators = [
            DataRequired()
        ]
    )
    requested_time = DateTimeField(
        "When do you need a pet sitter?", format='%m/%d/%y',
        default=datetime.datetime.now,
        validators = [
            DataRequired()
        ]
    )

class UpdatePostForm(Form):
    content = TextAreaField(
        "List all the details.",
        validators = [
            DataRequired()
        ]
    )
    requested_time = DateTimeField(
        "When do you need a pet sitter?", format='%m/%d/%y',
        default = datetime.datetime.now,
        validators = [
            DataRequired(
                message = 'Input the month, date, and year, e.g. 01/01/2000'
            )
        ]
    )

''' new pet '''
class PetForm(Form):
    name = StringField(
        "What is your pet's name?",
        validators = [
            DataRequired()
        ]
    )
    pet_type = StringField(
        "What type of animal is your pet?",
        validators = [
            DataRequired()
        ]
    )
    age = IntegerField(
        "How old is your pet?",
        validators = [
            DataRequired()
        ]
    )
    special_requirements = StringField(
        "Are there any special requirements a sitter needs to know about in order to take care of your pet?"
    )

''' new message '''
class MessageForm(Form):
    content = TextAreaField(
        "Type your message below.",
        validators = [
            DataRequired(),
            Length(min = 0, max = 500)
        ]
    )

class UserUpdateForm(Form):
    location = StringField(
        "Location",
        validators = [
            DataRequired()
        ]
    )
    bio = TextAreaField(
        "Bio"
    )
