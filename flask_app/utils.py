from datetime import timedelta

def convert_datetime(datetime):
	local = datetime - timedelta(hours=5)
	return local.strftime("%B %d, %Y %I:%M %p")