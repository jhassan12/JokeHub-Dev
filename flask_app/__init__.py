from flask import Flask, render_template, request, redirect, url_for
from flask_talisman import Talisman
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

from datetime import datetime
import os

from .client import LaughFactoryClient

import logging

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
laugh_factory_client = LaughFactoryClient()

from .users.routes import users
from .jokes.routes import jokes

def page_not_found(e):
    return render_template("error.html"), 404

def create_app(test_config=None):
    app = Flask(__name__)

    app.config["MONGODB_HOST"] = os.getenv("MONGODB_HOST")

    csp = {
        'default-src': '\'self\'',
        'img-src': ['\'self\'', "data:"],
        'style-src': ['\'self\'', 'unsafe-inline', 'pro.fontawesome.com', 'stackpath.bootstrapcdn.com'],
        'script-src': ['\'self\'', 'code.jquery.com', 'cdn.jsdelivr.net', 'stackpath.bootstrapcdn.com', 'unsafe-inline'],
        'font-src': ['\'self\'', 'pro.fontawesome.com']
    }

    Talisman(app, content_security_policy=csp)

    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(users)
    app.register_blueprint(jokes)
    
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app
