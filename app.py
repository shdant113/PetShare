from flask import Flask, g, render_template, flash, redirect, url_for
from flask_login import (LoginManager, login_user, logout_user,
login_required, current_user)
from flask_bcrypt import check_password_hash

import forms
import models
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
	try:
		return models.User.get(models.User.id == userid)
	except models.DoesNotExist:
		return None

@app.before_request
def before_request():
	g.db = models.DATABASE
	g.db.connect()

@app.after_request
def after_request(response):
	g.db.close()
	return response

@app.route('/')
def index():
	return 'this is an index route'

@app.route('/register', methods = ('GET', 'POST'))
def register_account():
	form = forms.RegisterForm()
	print(form, ' this is form')
	if form.validate_on_submit():
		print('we got to the if')
		models.User.create_a_user(
			username = form.username.data,
			password = form.password.data,
			email = form.email.data
		)
		print('we are making a user')
		return redirect(url_for('index'))
		print('we made a user')
		print('we redirected')
	return render_template('register.html', form = form)

@login_required
@app.route('/login')
def login():
	print('hi')	
	return 'you are here'
	

if __name__ == '__main__':
	models.init_database()
	try: 
		models.User.create_a_user(
			username = 'admin',
			email = 'admin@admin.com',
			password = 'admin',
			admin = True
		)
	except ValueError: 
		pass

app.run(debug = config.DEBUG, port = config.PORT)

