import json
from flask import jsonify, Blueprint, abort, make_response
from flask_restful import (Resource, Api, reqparse, inputs,
	fields, marshal, marshal_with, url_for)
from flask_login import (login_user, logout_user, login_required,
	current_user)

import models

user_fields = {
	'username': fields.String
}

class UserList(Resource):
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument(
			'username',
			required = True,
			help = 'No username provided',
			location = ['form', 'json']
		)
		self.reqparse.add_argument(
			'email',
			required = True,
			help = 'No email provided',
			location = ['form', 'json']
		)
		self.reqparse.add_argument(
			'display name',
			required = True,
			help = 'No display name provided',
			location = ['form', 'json']
		)
		self.reqparse.add_argument(
			'password',
			required = True,
			help = 'No input provided',
			location = ['form', 'json']
		)
		self.reqparse.add_argument(
			'confirm_password',
			required = True,
			help = 'No input provided',
			location = ['form', 'json']
		)
		super().__init__()

	def register(self):
		arguments = self.reqparse.parse_args()
		if arguments['password'] == arguments['confirm_password']:
			print(arguments, ' this is arguments')
			user = models.User.create_a_user(**arguments)
			login_user(user)
			return marshal(user, user_fields), 201
		return set_response(
			json.dumps({
				'error': 'Both passwords must match.'
			}), 400	
		)

users_api = Blueprint('resources.users', __name__)
api = Api(users_api)
api.add_resource(
    UserList,
    '/users',
    endpoint='users'
)



