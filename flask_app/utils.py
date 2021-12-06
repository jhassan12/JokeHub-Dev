from datetime import datetime
import pytz 
import tzlocal

def convert_datetime(utc_time):
	local_timezone = tzlocal.get_localzone()
	local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)	
	return local_time.strftime("%B %d, %Y %I:%M %p")