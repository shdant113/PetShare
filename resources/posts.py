from flask import jsonify, Blueprint, abort
from flask_restful import (Resource, Api, reqparse, fields, marshal,
	marshal_with, url_for)
from flask_login import login_required
import models

post_fields = {
	'id': fields.Integer,
	'content': fields.String
}