from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):

	username = StringField('username',validators=[DataRequired(),Length(min=3,max=16)])
	email = StringField('Email',validators=[DataRequired(),Email()])
	password =  PasswordField('password',validators=[DataRequired(),Length(min=5,max=30)])
	confirm_password = PasswordField('confirm password',validators=[DataRequired(),EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self,username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('This username is already exit!Please Chose a diffrent one')

	def validate_email(self,email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('This Email is already exit!Please Chose a diffrent one')



class LoginForm(FlaskForm):

	email = StringField('Email',validators=[DataRequired(),Email()])
	password =  PasswordField('password',validators=[DataRequired(),Length(min=5,max=30)])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):

	username = StringField('username',validators=[DataRequired(),Length(min=3,max=16)])
	email = StringField('Email',validators=[DataRequired(),Email()])
	submit = SubmitField('Update')
	picture = FileField('Update Profile Picture',validators=[FileAllowed(['jpg','png'])])

	def validate_username(self,username):
		if current_user.username != username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('This username is already exit!Please Chose a diffrent one')

	def validate_email(self,email):
		if current_user.email != email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('This Email is already exit!Please Chose a diffrent one')

class PostForm(FlaskForm):
	title = StringField('Title',validators=[DataRequired()])
	content = TextAreaField('Content',validators=[DataRequired()])
	submit = SubmitField('Post')

class RequestResetForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Email()])
	submit = SubmitField('Password Reset')

	def validate_email(self,email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError("There is not account with that email! You need to create a account")

class ResetPasswordForm(FlaskForm):
	password =  PasswordField('New password',validators=[DataRequired(),Length(min=5,max=30)])
	confirm_password = PasswordField('confirm New password',validators=[DataRequired(),EqualTo('password')])
	submit = SubmitField('Confirm')