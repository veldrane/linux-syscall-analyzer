import argparse;
import re;
import glob;
from elasticsearch import Elasticsearch;
from operator import itemgetter;

VERSION = "0.1";
logging = False;

def log(message):

	import time;
	global logging;

	if logging == False:
		return 0;

	localtime = time.asctime(time.localtime(time.time()));
	output = (localtime+' ---| '+message);
	print (output);
		
	return 0;



def parseargv():

	parser = argparse.ArgumentParser();
	parser.add_argument("directory", help="Working directory with raw strace dumps");
	parser.add_argument("-l", "--log", help="Enabling logging to terminal", action='store_true');
	args = parser.parse_args();
	args.directory = re.sub('(\/+)$','',args.directory);
	return args;

def gettracefiles(target):

	files = glob.glob(target+'/'+'*');
	tracelist = [];
	log("Loooking for strace files in directory "+target);

	for i in files:
		trace = open(i,'r');
		line = (trace.readline()).split(' ');
		syscall = line[1].split('(')[0];
		timestamp = float(line[0]);
		tracelist.append((timestamp,syscall,i));
		trace.close;

	tracelist=sorted(tracelist, key=itemgetter(0));
	log("Found "+(str(len(tracelist)))+" files");
	log("First file "+str((tracelist[0])[2])+" will be processed...");
	return tracelist;

args=parseargv();
logging=args.log
traces=gettracefiles(args.directory);
