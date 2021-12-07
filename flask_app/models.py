from flask_login import UserMixin
from . import db, login_manager
from . import config
import base64

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True, min_length=3, max_length=50)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True, min_length=8, max_length=50)
    joke_likes = db.StringField()
    comment_likes = db.StringField()

    def get_id(self):
        return self.username

class Joke(db.Document):
    author = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=3, max_length=500)
    date = db.DateTimeField(required=True)
    likes = db.IntField(required=True)

class Comment(db.Document):
    jokeid = db.StringField(required=True)
    author = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=3, max_length=500)
    date = db.DateTimeField(required=True)
    likes = db.IntField(required=True)