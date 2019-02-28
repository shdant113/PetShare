from flask import Flask, g, render_template, flash, redirect, url_for
from flask_login import (LoginManager, login_user, logout_user,
login_required, current_user)
from flask_bcrypt import check_password_hash

import forms
import models
import config

''' initialize program '''
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

''' login middleware '''
login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(userid):
	try:
		return models.User.get(models.User.id == userid)
	except models.DoesNotExist:
		return None

''' pool db connections '''
@app.before_request
def before_request():
	g.db = models.DATABASE
	g.db.connect()
	g.user = current_user

@app.after_request
def after_request(response):
	g.db.close()
	return response

##############
''' ROUTES '''
##############

''' 404 '''
@app.errorhandler(404)
def pet_404(e):
	return render_template('404.html'), 404

''' index/dashboard '''
@login_required
@app.route('/')
def dashboard():
	posts = models.Post.select()
	user = current_user
	return render_template('dashboard.html', posts = posts, user = user)

''' registration '''
@app.route('/register', methods = ('GET', 'POST'))
def register_account():
	# for post method --> pass data from form
	form = forms.RegisterForm()
	if form.validate_on_submit():
		models.User.create_a_user(
			username = form.username.data,
			display_name = form.display_name.data,
			location = form.location.data,
			password = form.password.data,
			email = form.email.data
		)
		user = models.User.get(models.User.username == form.username.data)
		login_user(user)
		return redirect(url_for('dashboard'))
	# for get method --> retrieve form
	return render_template('register.html', form = form)

''' logging in '''
@app.route('/login', methods = ('GET', 'POST'))
def login():
	form = forms.LoginForm()
	if form.validate_on_submit():
		try:
			 user = models.User.get(models.User.email == form.email.data)
		except models.DoesNotExist:
			flash('Your email or password does not match.')
		else:
			if check_password_hash(user.password, form.password.data):
				login_user(user)
				return redirect(url_for('dashboard'))
			else:
				flash('Your email or password does not match.')
	return render_template('login.html', form = form)

''' logging out '''
@login_required
@app.route('/logout')
def logout():
	# destroy our session
	logout_user()
	return redirect(url_for('dashboard'))

''' adding a new post '''
@login_required
@app.route('/new_post', methods = ('GET', 'POST'))
def new_post():
	form = forms.PostForm()
	user = models.User.select().where(models.User.id == current_user.id).get()
	pets = models.Pet.select().where(models.Pet.owner == user)

	petList = []
	for pet in pets:
		petList.append((pet.id, pet.name))
	
	form.pet.choices = petList

	if form.validate_on_submit():
		models.Post.create(
			user = g.user._get_current_object(),
			content = form.content.data.strip(),
			pet = form.pet.data,
			requested_time = form.requested_time.data
		)
		return redirect(url_for('dashboard'))
	return render_template('post.html', form = form)

''' add a new pet '''
@login_required
@app.route('/new_pet', methods = ('GET', 'POST'))
def new_pet():
	form = forms.PetForm()
	if form.validate_on_submit():
		models.Pet.create(
			name = form.name.data,
			age = form.age.data,
			pet_type = form.pet_type.data,
			special_requirements = form.special_requirements.data,
			owner = models.User.select().where(models.User.id == current_user.id).get()
		)
		return redirect(url_for('dashboard'))
	return render_template('add-pet.html', form = form)

''' show index of pets '''
@login_required
@app.route('/show')
def show():

	## THIS ROUTE IS FOR TESTING ONLY IT SHOULD NOT BE ON THE FINAL PRODUCT
	
	# if username and username != current_user.username:
	# 	user = (models.User.select()
	# 		.where(models.User.username ** username).get())
	# 	pets = user.pets
	# else: 
	user = models.User.select().where(models.User.id == current_user.id).get()
	pets = models.Pet.select()
		#.where(models.Pet.owner == user).get()
	return render_template('user_profile.html', user = user, pets = pets)


''' edit and update a pet '''
@login_required
@app.route('/update_pet/<id>', methods = ('GET', 'PUT'))
def update_pet():
	form = forms.PetForm()
	if form.validate_on_submit():
		models.Pet.update(
			name = form.name.data,
			age = form.age.data,
			pet_type = form.pet_type.data,
			special_requirements = form.special_requirements.data
		)	
		return redirect(url_for('dashboard'))
	return render_template('edit-pet.html', form = form)

''' delete a pet '''
@login_required
@app.route('/delete_pet/<id>', methods = ('GET', 'DELETE'))
def delete_pet(name):
	form = forms.DeletePetForm()
	if form.validate_on_submit():
		models.Pet.name.delete()
		return redirect(url_for('dashboard'))
	return render_template('delete-pet.html', form = form)

''' user profile '''
@app.route('/users/<id>')
def get_profile(id):
	user = models.User.select().where(models.User.id == current_user.id).get()
	pets = models.Pet.select().where(models.Pet.owner == user)
	posts = models.Post.select().where(models.Post.user == user)
	return render_template('user_profile.html', user = user, pets = pets,
	posts = posts)


''' accept a job -- click on post '''
# @login_required
# @app.route('/accept_job', methods = ('GET', 'POST'))
# def accept_job():
	
''' initialize database '''
if __name__ == '__main__':
    models.init_database()

app.run(debug = config.DEBUG, port = config.PORT)

