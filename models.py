
from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash
import datetime

DATABASE = SqliteDatabase('')

class User(UserMixin, Model):
	username = CharField(unique = True)
	email = CharField(unique = True)
	password = CharField(max_length = 30)
	date_joined = DateTimeField(default = datetime.datetime.now)
	admin_status = BooleanField(default = False)

class Meta:
	database = DATABASE

@classmethod
def create_a_user(cls, username, email, password, admin = False):
	try:
		cls.create(
			username = username,
			email = email,
			password = generate_password_hash(password),
			admin_status = admin
		)
	except IntegrityError:
		raise ValueError('User already exists.')

def init_database():
	DATABASE.connect()
	DATABASE.create_tables([User], safe = True)
	DATABASE.close()


