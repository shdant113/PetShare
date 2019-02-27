from flask import jsonify, Blueprint, abort
from flask_restful import (Resource, Api, reqparse, fields, marshal,
	marshal_with, url_for)
from flask_login import login_required
import models

pets_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'pet_type': fields.String,
	'age': fields.Integer,
	'special_requirements': fields.String
}

def pets_error(pet_id):
	try:
		pet = models.Pet.get(models.Pet.id == pet.id)
	except models.Pet.DoesNotExist:
		abort(404)
	else:
		return pet

class PetList(Resource):
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument(
			'name',
			required = False,
			help = 'No pet name provided.',
			location = ['form', 'json']
		)
		self.reqparse.add_argument(
			'what kind of animal?',
			required = False,
			help = 'No pet type provided.',
			location = ['form', 'json']
		)
		self.reqparse.add_argument(
			'age',
			required = False,
			help = 'No pet age provided.',
			location = ['form', 'json']
		)
		self.reqparse.add_argument(
			'special requirements',
			required = False,
			location = ['form', 'json']
		)
		super().__init__()

	@login_required
	def get(self):
		pets = [marshal(pets, pets_fields) for pet in models.Pet.select()]
		return {'pets': pets}

	def post(self):
		arguments = self.reqparse.parse_args()
		print(arguments, ' we are hitting args')
		parsedPet = [marshal(models.Pet.create(**arguments), pets_fields)]
		return parsedPet

class Pet(Resource):
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument(
			"What is your pet's name?",
			required = False,
			help = 'Please provide a name',
			location = ['form', 'json']
		)
		self.reqparse.add_argument(
			"What type of animal is your pet?",
			required = False,
			help = 'Please tell us what type of animal your pet is',
			location = ['form', 'json']
		)
		self.reqparse.add_argument(
			"How old is your pet?",
			required = False,
			help = 'Please tell us how old your pet is',
			location = ['form', 'json']
		)
		self.reqparse.add_argument(
			"Are there any special requirements a sitter needs to know about in order to take care of your pet?",
			required = False,
			location = ['form', 'json']
		)
		super().__init__()

	@marshal_with(pets_fields)
	def get(self, id):
		return pets_error

	def put(self, id):
		arguments = self.reqparse.parse_args()
		query = models.Pet.update(**arguments).where(models.Pet.id == id)
		query.execute()
		parsedQuery = [marshal(models.Pet.get(models.Pet.id == id), pets_fields)]
		return parsedQuery

	def delete(self, id):
		arguments = self.reqparse.parse_args()
		query = models.Pet.delete().where(models.Pet.id == id)
		query.execute()
		return 'deleted the pet'

pets_api = Blueprint('resources.pets', __name__)
api = Api(pets_api)
api.add_resource(
	PetList,
	'/pets',
	endpoint = 'pets'
)
api.add_resource(
	Pet,
	'/pets/<int:id>',
	endpoint = 'pet'
)