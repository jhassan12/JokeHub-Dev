from flask import Blueprint, redirect, url_for, render_template, flash, request, abort
from flask_login import current_user, login_required, login_user, logout_user

import bcrypt

from ..forms import RegistrationForm, LoginForm, ChangeUsernameForm
from ..models import User

from ..models import User, Joke, Comment

users = Blueprint('users', __name__, static_folder='static', template_folder='templates')

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("jokes.index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed, joke_likes="", comment_likes="")
        user.save()

        flash("Successfully created account. Please login with your credentials.", "success")
        return redirect(url_for("users.login"))

    return render_template("register.html", title="Register", form=form)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("jokes.index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            return redirect(url_for("jokes.index"))
        else:
            flash("Login failed. Check your username and/or password", "danger")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login", form=form)

@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("users.login"))

@users.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    user_likes = current_user.joke_likes
    user_likes_arr = user_likes.split(",")

    user = User.objects(username=username).first()

    if not user:
        abort(404)

    jokes = Joke.objects(author__in=User.objects(username=username)).order_by("-date")

    form = ChangeUsernameForm()

    if form.validate_on_submit():
        new_username = form.username.data

        if User.objects(username=new_username).first():
            flash('User already exists with that username.', 'danger')
        else:
            current_user.update(username=new_username)
            current_user.save()
            flash('Successfully changed username!', 'success')

            return redirect(url_for('users.profile', username=username))

    for joke in jokes:
        joke.date = joke.date.strftime("%B %d, %Y at %H:%M:%S")
        joke.can_delete = joke.author.username == current_user.username
        joke.heart_filled_in = str(joke.id) in user_likes_arr

    show_form = current_user.username == username

    return render_template("profile.html", title="Profile", jokes=jokes, show_form=show_form, form=form, user=user)

@users.route("/wipe-out")
def wipe_out():
    logout_user()

    User.drop_collection()
    Joke.drop_collection()
    Comment.drop_collection()

    return redirect(url_for('users.login'))

@users.route("/about")
def about():
    return render_template("about.html")




    