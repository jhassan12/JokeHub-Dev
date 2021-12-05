from datetime import datetime
from flask import Blueprint, render_template, url_for, redirect, request, flash, abort
from flask_login import current_user, login_required

import re

from .. import laugh_factory_client

from ..utils import convert_datetime

from ..models import User

from ..forms import JokeForm, JokeCommentForm, SearchForm
from ..models import User, Joke, Comment


jokes = Blueprint('jokes', __name__, static_folder='static', template_folder='templates')

@jokes.route("/", methods=["GET"])
@login_required
def index():
	user_likes = current_user.joke_likes
	user_likes_arr = user_likes.split(",")

	created_jokes = Joke.objects(author__in=User.objects(username=current_user.username))

	liked_jokes = []

	for jokeid in user_likes_arr:
		if jokeid:
			joke = Joke.objects(id=jokeid).first()
			
			if joke and joke.author.username != current_user.username:
				liked_jokes.append(joke)

	jokes = list(created_jokes) + liked_jokes
	jokes.sort(key=lambda x: x.date, reverse=True)

	for joke in jokes:
		joke.date = convert_datetime(joke.date)
		joke.can_delete = joke.author.username == current_user.username
		joke.heart_filled_in = str(joke.id) in user_likes_arr

	return render_template("index.html", jokes=jokes)

@jokes.route("/all_jokes", methods=["GET"])
@login_required
def all_jokes():
	user_likes = current_user.joke_likes
	user_likes_arr = user_likes.split(",")

	jokes = Joke.objects().order_by("-date")

	for joke in jokes:
		joke.date = convert_datetime(joke.date)
		joke.can_delete = joke.author.username == current_user.username
		joke.heart_filled_in = str(joke.id) in user_likes_arr

	return render_template("all_jokes.html", jokes=jokes)

@jokes.route("/create", methods=["GET", "POST"])
@login_required
def create():
	form = JokeForm()

	if form.validate_on_submit():
		joke = Joke(
			author=current_user._get_current_object(),
			content=form.content.data,
			date=datetime.now(),
			likes=0
		)

		joke.save()

		return redirect(url_for('jokes.index'))

	return render_template("create_joke.html", title="Create Joke", form=form)

@jokes.route("/update-joke-likes/<jokeid>/")
@login_required
def update_joke_likes(jokeid):
	joke = None

	try:
		joke = Joke.objects(id=jokeid).first()
	except:
		abort(404)

	user_likes = current_user.joke_likes
	user_likes_arr = user_likes.split(",")

	if joke:
		if jokeid in user_likes_arr:
			user_likes_arr.remove(jokeid)
			current_user.update(joke_likes=','.join(user_likes_arr))
			current_user.save()

			joke.update(likes=max(joke.likes - 1, 0))
			joke.save()
		else:
			user_likes_arr.append(jokeid)
			current_user.update(joke_likes=','.join(user_likes_arr))
			current_user.save()

			joke.update(likes=joke.likes + 1)
			joke.save()
	else:
		abort(404)

	return redirect(request.referrer)

@jokes.route("/update-comment-likes/<commentid>")
@login_required
def update_comment_likes(commentid):
	comment = None

	try:
		comment = Comment.objects(id=commentid).first()
	except:
		abort(404)

	user_likes = current_user.comment_likes
	user_likes_arr = user_likes.split(",")

	if comment:
		if commentid in user_likes_arr:
			user_likes_arr.remove(commentid)
			current_user.update(comment_likes=','.join(user_likes_arr))
			current_user.save()

			comment.update(likes=max(comment.likes - 1, 0))
			comment.save()
		else:
			user_likes_arr.append(commentid)
			current_user.update(comment_likes=','.join(user_likes_arr))
			current_user.save()

			comment.update(likes=comment.likes + 1)
			comment.save()
	else:
		abort(404)

	return redirect(url_for('jokes.joke', jokeid=comment.jokeid))

@jokes.route("/joke/<jokeid>", methods=["GET", "POST"])
@login_required
def joke(jokeid):
	user_joke_likes = current_user.joke_likes
	user_joke_likes_arr = user_joke_likes.split(",")

	user_comment_likes = current_user.comment_likes
	user_comment_likes_arr = user_comment_likes.split(",")

	joke = None

	try:
		joke = Joke.objects(id=jokeid).first()
	except:
		abort(404)

	if not joke:
		abort(404)

	form = JokeCommentForm()

	if form.validate_on_submit():
		comment = Comment(
			jokeid=jokeid,
			author=current_user._get_current_object(),
			content=form.content.data,
			date=datetime.now(),
			likes=0
		)

		comment.save()

		return redirect(url_for('jokes.joke', jokeid=jokeid))

	joke.heart_filled_in = str(joke.id) in user_joke_likes_arr

	comments = Comment.objects(jokeid=jokeid).order_by('-date')

	for comment in comments:
		comment.heart_filled_in = str(comment.id) in user_comment_likes_arr
		comment.date = convert_datetime(comment.date)
		comment.can_delete = comment.author.username == current_user.username

	joke.date = convert_datetime(joke.date)
	joke.can_delete = joke.author.username == current_user.username

	return render_template("joke.html", joke=joke, form=form, title="Joke", comments=comments)

@jokes.route("/delete-joke/<jokeid>/")
@login_required
def delete_joke(jokeid):
	joke = None

	try:
		joke = Joke.objects(id=jokeid).first()
	except:
		abort(404)

	if not joke:
		abort(404)

	if joke.author.username != current_user.username:
		flash('You do not have permission to perform this action.', 'danger')
		return redirect(url_for("jokes.index"))

	joke.delete()

	users = User.objects()

	for user in users:
		user_likes = user.joke_likes
		user_likes_arr = user_likes.split(",")

		if jokeid in user_likes_arr:
			user_likes_arr.remove(jokeid)
			user.update(joke_likes=','.join(user_likes_arr))
			user.save()

	Comment.objects(jokeid=jokeid).delete()

	if url_for("jokes.joke", jokeid=jokeid) in request.referrer:
		return redirect(url_for("jokes.index"))

	return redirect(request.referrer)

@jokes.route("/delete-comment/<commentid>")
@login_required
def delete_comment(commentid):
	comment = None

	try:
		comment = Comment.objects(id=commentid).first()
	except:
		abort(404)
	
	if not comment:
		abort(404)

	if comment.author.username != current_user.username:
		flash('You do not have permission to perform this action.', 'danger')
		return redirect(url_for("jokes.index"))

	comment.delete()

	users = User.objects()

	for user in users:
		user_likes = user.comment_likes
		user_likes_arr = user_likes.split(",")

		if commentid in user_likes_arr:
			user_likes_arr.remove(commentid)
			user.update(comment_likes=','.join(user_likes_arr))
			user.save()

	return redirect(url_for('jokes.joke', jokeid=comment.jokeid))

@jokes.route("/laugh-factory-jokes/<upper_limit>")
def laugh_factory_jokes(upper_limit):
	if not upper_limit.isnumeric() or int(upper_limit) < 1:
		flash('An error has occured.')
		return render_template(url_for('laugh_factory_jokes.html', jokes=[]))

	lim = int(upper_limit)
	jokes, last_page = laugh_factory_client.load_pages(lim)

	return render_template('laugh_factory_jokes.html', jokes=jokes, upper_limit=lim, title="Laugh Factory Jokes", last_page=last_page)

@jokes.route("/search", methods=["GET", "POST"])
@login_required
def search():
	form = SearchForm()

	if form.validate_on_submit():
		query = form.query.data.strip()

		if len(query) < 1:
			flash('Query too short.')
			return redirect(url_for("jokes.search"))

		return redirect(url_for("jokes.search_results", query=query))

	return render_template("search.html", form=form)

@jokes.route("/search-results/<query>")
@login_required
def search_results(query):
	user_likes = current_user.joke_likes
	user_likes_arr = user_likes.split(",")

	regex = re.compile(f".*{query}.*", re.IGNORECASE)
	jokes = Joke.objects(content=regex).order_by("-date")

	for joke in jokes:
		joke.date = convert_datetime(joke.date)
		joke.can_delete = joke.author.username == current_user.username
		joke.heart_filled_in = str(joke.id) in user_likes_arr

	return render_template("search_results.html", jokes=jokes, query=query, count=len(jokes))

