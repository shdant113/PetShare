
from flask import Flask, g
# from flask import render_template, flash, redirect, url_for
# from flask_login import (LoginManager, login_user, logout_user,
# login_required, current_user)
# from flask_bcrypt import check_password_hash

# import forms
# import models
import config

app = Flask(__name__)

# @app.before_request
# def before_request():
# 	g.db = models.DATABASE
# 	g.db.connect()

# @app.after_request
# def after_request(response):
# 	g.db.close()
# 	return response

@app.route('/')
def index():
	return 'this is an index route'

# if __name__ = '__main__':
# 	models.init_database()
# 	try: 
# 		models.User.create_a_user(
# 			username = 'admin',
# 			email = 'admin@admin.com',
# 			password = 'admin',
# 			admin = True
# 		)
# 	except ValueError: 
# 		pass

app.run(debug = config.DEBUG, port = config.PORT)

