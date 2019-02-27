from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash
import datetime

DATABASE = SqliteDatabase('petsdb.sqlite')

class User(UserMixin, Model):
	username = CharField(unique = True)
	display_name = CharField(default = username)
	email = CharField(unique = True)
	password = CharField(max_length = 30)
	date_joined = DateTimeField(default = datetime.datetime.now)
	admin_status = BooleanField(default = False)
	bio = TextField()
	location = CharField()
	# schedule = ForeignKeyField(Post, related_name = 'schedule_user')
	notifications = CharField(null = True)

	class Meta:
		database = DATABASE

	@classmethod
	def create_a_user(cls, username, email, password, admin = False):
		print('we are creating a user')
		try:
			print('we are in the try block')
			cls.create(
				username = username,
				email = email,
				password = generate_password_hash(password),
				admin_status = admin
			)
		except IntegrityError:
			print('there was an error')
			raise ValueError('user already exists')


class Pet(Model):
	name = CharField()
	pet_type = CharField() # enum/CREATE TYPE
	age = IntegerField()
	created_on = DateTimeField(default = datetime.datetime.now)
	owner = ForeignKeyField(User, related_name = 'owner_pet')
	special_requirements = TextField()

	class Meta:
		database = DATABASE

	@classmethod
	def create_a_pet(cls, name, pet_type, age, special_requirements):
		try:
			cls.create(
				name = name,
				pet_type = pet_type,
				age = age,
				special_requirements = special_requirements
			)
		except IntegrityError:
			raise ValueError('Invalid inputs.')


class Post(Model):
	timestamp = DateTimeField(default = datetime.datetime.now)
	user = ForeignKeyField(User, backref = 'posts')
	pet = ForeignKeyField(Pet, backref = 'posts')
	requested_time = DateTimeField()
	sitter = ForeignKeyField(User, null = True, backref = 'posts')
	content = TextField()
	job_accepted = BooleanField(default = False)

	class Meta:
		database = DATABASE
		order_by = ('-timestamp',)

def init_database():
	DATABASE.connect()
	DATABASE.create_tables([User, Pet, Post], safe = True)
	DATABASE.close()


