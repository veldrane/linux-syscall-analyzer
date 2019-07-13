import settings;
import datetime;

def log(message):

	if settings.logging == False:
		return 0;

	localtime = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
	output = (localtime+' ---| '+message);
	print (output);

	return 0;


def debug(message):

	if settings.debugging == False:
		return 0;

	print (message);

	return 0;
