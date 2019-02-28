from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash
import datetime

DATABASE = PostgresqlDatabase(
	'pets',
	user = 's_admin',
	password = 'administrator'
)

class User(UserMixin, Model):
	username = CharField(unique = True)
	display_name = CharField(default = username)
	email = CharField(unique = True)
	password = CharField(max_length = 100)
	date_joined = DateTimeField(default = datetime.datetime.now)
	admin_status = BooleanField(default = False)
	bio = TextField(null=True)
	location = CharField(null=True)
	# schedule = ForeignKeyField(Post, related_name = 'schedule_user')
	notifications = CharField(null = True)

	class Meta:
		database = DATABASE

	@classmethod
	def create_a_user(cls, username, email, display_name, location, password, admin = False):
		try:
			cls.select().where(cls.username == username).get()
			cls.select().where(cls.display_name == display_name).get()
			cls.select().where(cls.email == email).get()
		except cls.DoesNotExist:
			user = cls(
				username = username, 
				email = email, 
				display_name = display_name,
				location = location, 
				admin_status = admin
			)
			user.password = generate_password_hash(password)
			user.save()
			return user
		except IntegrityError:
			raise ValueError('user already exists')

	@classmethod
	def get_user(self, id):
		return User.select().where(
			(User.id == self.id)
		)

	@classmethod
	def show_pets(self):
		return Pet.select().where(
			(Pet.owner == self)
		)


class Pet(Model):
	name = CharField()
	pet_type = CharField() # enum/CREATE TYPE
	age = IntegerField()
	created_on = DateTimeField(default = datetime.datetime.now)
	owner = ForeignKeyField(User, related_name = 'owner_pet')
	special_requirements = TextField()

	class Meta:
		database = DATABASE



class Post(Model):
	timestamp = DateTimeField(default = datetime.datetime.now)
	user = ForeignKeyField(User, backref = 'posts')
	pet = ForeignKeyField(Pet, backref = 'posts')
	requested_time = DateField()
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


