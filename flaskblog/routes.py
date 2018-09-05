from flaskblog.models import User, Post
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog.Forms import (LoginForm, RegistrationForm, UpdateAccountForm
							, PostForm, RequestResetForm, ResetPasswordForm)
from flaskblog import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image
from flask_mail import Message

@app.route("/")
@app.route("/home")
def home():
	page = request.args.get('page',1,type=int)
	data = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
	#data.reverse()
	return render_template('home.html',posts=data,title='Home')

@app.route("/about")
def about():
	return render_template('about.html',title='about')
@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_psswd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data,email=form.email.data,password=hashed_psswd)
		db.session.add(user)
		db.session.commit()
		#show flashed messages if form are validate
		flash('Your Acoount has been created!.Your now able to login','success')
		#after creating account we redirect user to home page 
		return redirect(url_for('login'))
	return render_template('register.html',title='Registration', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password,form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check Email and password','danger')
	return render_template('login.html',title='Login',form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('login'))

def save_picture(form_picture):
	f_hex = secrets.token_hex(8)
	_,f_ext = os.path.splitext(form_picture.filename)
	picture_fn = f_hex+f_ext
	picture_path = os.path.join(app.root_path,'static/profil_pics',picture_fn)
	output_size = (125,125)
	ig = Image.open(form_picture)
	ig.thumbnail(output_size)
	ig.save(picture_path)
	return picture_fn

@app.route('/account',methods=['GET','POST'])
@login_required
def account():
	image_file = url_for('static',filename='profil_pics/'+current_user.image_file)
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!','success')
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email

	return render_template('account.html',title='Account',image_file=image_file, form=form)

@app.route('/new/post',methods=['GET','POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data,content=form.content.data,author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your Post has been posted!','success')
		return redirect(url_for('home'))
	return render_template('new_post.html',title='NEW POST',form=form, legend='New Post')

@app.route('/new/<int:post_id>',methods=['GET','POST'])
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html',title=post.title,post=post)

@app.route('/new/<int:post_id>/update',methods=['GET','POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Your post has been updated!','success')
		return redirect(url_for('post',post_id=post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('new_post.html',title='Update Post',form=form, legend='Update Post')

@app.route('/new/<int:post_id>/delete',methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!','success')
	return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user(username):
	page = request.args.get('page',1,type=int)
	user = User.query.filter_by(username=username).first_or_404()
	data = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
	
	return render_template('user_post.html',posts=data,title='User Post',user=user)

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request',sender='khaliayoub9@gmail.com',recipients=[user.email])
	msg.body = f'''To reset your passwor,please click on the following link:
{url_for('reset_token',token=token, _external=True)}
if you did not make that request,then simply ignore this email.Thank you!
'''
	mail.send(msg)

@app.route('/reset_password',methods=['POST','GET'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset your password','info')
		return redirect(url_for('login'))
	return render_template('reset_request.html',title='Reset Request',form=form)

@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is invalid or expired token!','warning')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_psswd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_psswd
		db.session.commit()
		#show flashed messages if form are validate
		flash('Your password has been updated!','success')
		#after creating account we redirect user to home page 
		return redirect(url_for('login'))
	return render_template('resetToken.html',title='Reset Password',form=form)
