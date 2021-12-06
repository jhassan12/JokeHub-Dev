from datetime import timedelta
import os

def convert_datetime(datetime):
	is_prod = os.environ.get('IS_HEROKU', None)

	if is_prod:
		# Atlas uses UTC, so here I'm just converting to EST.
		datetime = datetime - timedelta(hours=5)

	return datetime.strftime("%B %d, %Y %I:%M %p")