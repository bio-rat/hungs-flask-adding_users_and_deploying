from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)
    scores = db.relationship('Score', backref='user', lazy='dynamic')
    

class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)

class Score(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  wpm = db.Column(db.Integer, nullable=False)
  excerpt_id = db.Column(db.Integer, db.ForeignKey('excerpt.id'), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Excerpt(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  text = db.Column(db.String(200), unique=True, nullable=False)
  scores = db.relationship('Score', backref='excerpt', lazy='dynamic')


# setup login managerF
login_manager = LoginManager()
# login_manager.login_view = 'facebook.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.request_loader
def load_user_from_request(request):
    # Login Using our Custom Header
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Token ', '', 1)
        token = Token.query.filter_by(uuid=api_key).first()
        if token:
            return token.user

    return None
