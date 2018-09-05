from datetime import datetime
from flaskblog import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer 

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

#Structure of our Tables
#the extension login_manager expect that a user have certains attribute and methods:
#isAuthenticated, isActive, isAnanymos, getID
#UserMixin give us all this common methods
class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(16), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	posts = db.relationship('Post', backref='author', lazy=True) #one-to-many a user can have a lot of posts 
	
	def get_reset_token(self,expires_sec=1800):
		s = Serializer(app.config['SECRET_KEY'],expires_sec)
		token = s.dumps({'user_id':self.id}).decode('utf-8')
		return token

	@staticmethod	
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User({self.username},{self.email},{self.image_file})"

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, default=datetime.utcnow,nullable=False)
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #relationship to User Model

	def __repr__(self):
		return f"Post({self.title},{self.date_posted})"
