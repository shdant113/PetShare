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