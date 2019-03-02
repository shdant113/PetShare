import os
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
@app.route('/')
def dashboard():
	# if user is not logged in, redirect to login screen
	if current_user.is_anonymous:
		return redirect(url_for('login'))
	else: 
		# get posts, the logged in user, and any messages sent
		posts = models.Post.select()
		user = current_user
		received_messages = models.Message.select().where(models.Message.recipient == user.id)
		messages = received_messages.select().where(models.Message.unread == True)
		if messages:
			# if the logged in user was the recipient of the messages sent
			if user.id == models.Message.recipient:
				# and if there are posts, render normal dashboard template
				if posts:
					return render_template('dashboard.html', unread = True, posts = posts, user = user)
				# if there are no posts, render empty dashboard template
				else:
					return render_template('dashboard-empty.html', unread = True, user = user)
			else:
				if posts:
					return render_template('dashboard.html', unread = False, posts = posts, user = user)
				else:
					return render_template('dashboard-empty.html', unread = False, user = user)
		else:
			if posts:
				return render_template('dashboard.html', unread = False, posts = posts, user = user)
			else:
				return render_template('dashboard-empty.html', unread = False, user = user)

''' registration '''
@app.route('/register', methods = ('GET', 'POST'))
def register_account():
	# for post method --> pass data from form
	form = forms.RegisterForm()
	if form.validate_on_submit():
		# register the new user
		models.User.create_a_user(
			username = form.username.data,
			display_name = form.display_name.data,
			location = form.location.data,
			password = form.password.data,
			email = form.email.data
		)
		user = models.User.get(models.User.username == form.username.data)
		# log in newly registered user, send them to dashboard
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
		# if the user's credential does not exist:
		except models.DoesNotExist:
			flash('Your email or password does not match.')
		# if the user's credential exists:
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
	# destroy session, redirect to login screen
	logout_user()
	return redirect(url_for('login'))

''' user clicked delete user button, send to confirmation page '''
@login_required
@app.route('/users/<id>/are_you_sure')
def delete_route_to_confirm(id):
	user = models.User.select().where(models.User.id == id)
	return render_template('confirm-delete-profile.html', user = user, id = id)	

''' after confirmation, delete a user '''
@login_required
@app.route('/users/<id>/delete', methods = ('GET', 'DELETE'))
def delete_user(id):
	u = models.User.select().where(models.User.id == id).get()
	if u == current_user:
		# delete user's posts
		posts = models.Post.delete().where(models.Post.user == id)
		posts.execute()
		# delete user's pets
		pets = models.Pet.delete().where(models.Pet.owner == id)
		pets.execute()
		# remove the user's id from the messages they have sent so our model doesn't break if a user does not exist
		sent_messages = models.Message.delete().where(models.Message.sender == id)
		sent_messages.execute()
		# "" from messages they have received ""
		received_messages = models.Message.delete().where(models.Message.recipient == id)
		received_messages.execute()
		# destroy user
		user = models.User.delete().where(models.User.id == id)
		user.execute()
		# destroy user's session
		logout_user()
		return redirect(url_for('login'))
	else:
		return render_template('404.html')

'''edit and update a user'''
@login_required
@app.route('/users/<id>/edit', methods = ('GET', 'POST'))
def update_user(id):
	user = models.User.select().where(models.User.id == id).get()
	if user == current_user:
		# if the user is the user logged in, get the update form
		form = forms.UserUpdateForm(
			location = user.location,
			bio = user.bio
		)
		if form.validate_on_submit():
			# update the user
			u = models.User.update(
				location = form.location.data,
				bio = form.bio.data
			).where(models.User.id == id)
			u.execute()
			return redirect(url_for('get_profile', id = id))
		return render_template('edit-user.html', form=form, user=user)
	else:
		return render_template('404.html')

''' adding a new post '''
@login_required
@app.route('/new_post', methods = ('GET', 'POST'))
def new_post():
	form = forms.PostForm()
	user = models.User.select().where(models.User.id == current_user.id).get()
	pets = models.Pet.select().where(models.Pet.owner == user)
	# list of dropdown choices from user's registered pets for the pet the user is posting about
	petList = []
	for pet in pets:
		petList.append((pet.id, pet.name))
	form.pet.choices = petList
	if form.validate_on_submit():
		# create post
		models.Post.create(
			user = g.user._get_current_object(),
			content = form.content.data.strip(),
			pet = form.pet.data,
			requested_time = form.requested_time.data
		)
		return redirect(url_for('dashboard'))
	return render_template('post.html', form = form)

''' removing a post when a job is accepted '''
@login_required
@app.route('/posts/<id>/delete', methods = ('GET', 'DELETE'))
def delete_post(id):
	post = models.Post.delete().where(models.Post.id == id)
	# get user id so that we can return the user to their profile instead of the dashboard after they erase a post 
	# --> button that hits route is only accessible from user profile
	userid = models.User.select().where(models.User.id == current_user.id).get()
	post.execute()
	return redirect(url_for('get_profile', id = userid))

''' edit a post '''
@login_required
@app.route('/posts/<id>/edit', methods=('GET', 'POST'))
def update_post(id):
	post = models.Post.select().where(models.Post.id == id).get()
	# as above, get user id so they can be redirected to their profile
	userid = models.User.select().where(models.User.id == current_user.id).get()
	if current_user == post.user:
		form = forms.UpdatePostForm(
			content = post.content,
		)
		if form.validate_on_submit():
			p = models.Post.update(
				content = form.content.data,
				requested_time = form.requested_time.data
			)
			p.execute()
			return redirect(url_for('get_profile', id = userid))
		return render_template('edit-post.html', form=form)
	else:
		return render_template('404.html')

''' add a new pet '''
@login_required
@app.route('/new_pet', methods = ('GET', 'POST'))
def new_pet():
	form = forms.PetForm()
	if form.validate_on_submit():
		# create new pet
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
	# get pet by id
	pet = models.Pet.select().where(models.Pet.id == id).get()
	return render_template('show-pet.html', pet = pet)
	
''' edit and update a pet '''
@login_required
@app.route('/pets/<id>/edit', methods = ('GET', 'POST'))
def update_pet(id):
	pet = models.Pet.select().where(models.Pet.id == id).get()
	if pet.owner == current_user:
		form = forms.PetForm(
			name = pet.name,
			pet_type = pet.pet_type,
			age = pet.age,
			special_requirements = pet.special_requirements
		)
		if form.validate_on_submit():
			p = models.Pet.update(
				name = form.name.data,
				age = form.age.data,
				pet_type = form.pet_type.data,
				special_requirements = form.special_requirements.data
			).where(models.Pet.id == id)
			p.execute()
			return redirect(url_for('show_pet', id = id))
		return render_template('edit-pet.html', form=form, pet=pet)
	else:
		return render_template('404.html')

''' delete a pet '''
@login_required
@app.route('/pets/<id>/delete', methods = ('GET', 'DELETE'))
def delete_pet(id):
	# delete the posts that were about this pet
	posts = models.Post.delete().where(models.Post.pet == id)
	posts.execute()
	# delete the pet
	pet = models.Pet.delete().where(models.Pet.id == id)
	pet.execute()
	return redirect(url_for('dashboard'))

''' view user profile '''
@login_required
@app.route('/users/<id>')
def get_profile(id):
	# if the user trying to access someone else's profile
	if id != current_user.id:
		user = models.User.select().where(models.User.id == id).get()
		session_user = current_user
	# if they want to see their own profile
	else:
		session_user = current_user.id
		user = session_user
	# get pets, posts
	pets = models.Pet.select().where(models.Pet.owner == user)
	posts = models.Post.select().where(models.Post.user == user)
	return render_template('user_profile.html', user = user, session_user = session_user, 
		pets = pets, posts = posts)

''' send a message '''
@login_required
@app.route('/send/<recipient>', methods = ('GET', 'POST'))
def send_message(recipient):
	# get the recipient of the message, get the current user, and render the send message form
	user = models.User.select().where(models.User.id == recipient).get()
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
	# get messages the user has received
	messages = models.Message.select().where(models.Message.recipient == current_user.id)
	if messages:
		# upon opening inbox, update unread property to false to remove the unread message notification
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
	
''' for deployment on heroku '''
if 'ON_HEROKU' in os.environ:
	print('deployed ')
	models.init_database()

''' initialize database '''
if __name__ == '__main__':
    models.init_database()

''' only needs to be run for local testing -- gunicorn does this on heroku '''
# app.run(debug = config.DEBUG, port = config.PORT)