from flask import Flask, g, render_template, flash, redirect, url_for
from flask_login import (LoginManager, login_user, logout_user,
login_required, current_user)
from flask_bcrypt import check_password_hash

import forms
import models
import config

''' TO DO '''

'''

-- build route to individual pets off user profile? DONE
-- attach crud routes to each pet DONE
-- add delete button for messages DONE
-- fix inbox DONE

-- design all templates
-- style?
-- semantics?

-- deploy

'''

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
	messages = models.Message.select().where(models.Message.unread == True)
	if messages:
		flash('You have unread messages!')
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

''' show a pet '''
@login_required
@app.route('/pets/<id>')
def show_pet(id):
	pet = models.Pet.select().where(models.Pet.id == id).get()
	return render_template('show-pet.html', pet = pet)
	

''' edit and update a pet '''
@login_required
@app.route('/pets/<id>/edit', methods = ('GET', 'POST'))
def update_pet(id):
	pet = models.Pet.select().where(models.Pet.id == id).get()
	print('boutta print this pet')
	print(pet)
	form = forms.PetForm(
		name = pet.name,
		pet_type = pet.pet_type,
		age = pet.age,
		special_requirements = pet.special_requirements
	)
	print(form.data)
	if form.validate_on_submit():
		p = models.Pet.update(
			name = form.name.data,
			age = form.age.data,
			pet_type = form.pet_type.data,
			special_requirements = form.special_requirements.data
		).where(models.Pet.id == id)
		p.execute()
		print('save me')
		print(p)
		return redirect(url_for('dashboard'))
	return render_template('edit-pet.html', form=form, pet=pet)

''' delete a pet '''
@login_required
@app.route('/pets/<id>/delete', methods = ('GET', 'DELETE'))
def delete_pet(id):
	print('yo')
	posts = models.Post.delete().where(models.Post.pet == id)
	posts.execute()
	pet = models.Pet.delete().where(models.Pet.id == id)
	pet.execute()
	return redirect(url_for('dashboard'))

''' user profile '''
@app.route('/users/<id>')
def get_profile(id):
	if id != current_user.id:
		user = models.User.select().where(models.User.id == id).get()
		session_user = current_user
	else:
		session_user = current_user.id
		user = session_user
	pets = models.Pet.select().where(models.Pet.owner == user)
	posts = models.Post.select().where(models.Post.user == user)
	return render_template('user_profile.html', user = user, session_user = session_user, 
		pets = pets, posts = posts)

''' send a message '''
@login_required
@app.route('/send/<recipient>', methods = ('GET', 'POST'))
def send_message(recipient):
	user = models.User.select().where(models.User.username == recipient).get()
	current = models.User.select().where(models.User.username == current_user.username).get()
	form = forms.MessageForm()
	if form.validate_on_submit():
		models.Message.create(
			content = form.content.data,
			sender = current,
			recipient = user
		)
		return redirect(url_for('dashboard'))
	return render_template('send_message.html', form = form, recipient = recipient)

''' view your messages '''
@login_required
@app.route('/messages')
def read_message():
	messages = models.Message.select().where(models.Message.recipient == current_user.id)
	if messages:
		messages_to_update = models.Message.select().where(
			models.Message.recipient == current_user.id
			and models.Message.unread == True)
		if messages_to_update:
			update = models.Message.update(unread = False)
			update.execute()
		return render_template('view_message.html', messages = messages)
	else:
		return render_template('no_messages.html')
	

''' delete a message '''
@login_required
@app.route('/messages/<id>/delete', methods = ('GET', 'DELETE'))
def delete_message(id):
	message = models.Message.delete().where(models.Message.id == id)
	message.execute()
	return redirect(url_for('read_message'))
	
''' initialize database '''
if __name__ == '__main__':
    models.init_database()

app.run(debug = config.DEBUG, port = config.PORT)