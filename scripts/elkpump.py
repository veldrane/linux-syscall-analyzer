# MAIN program

import argparse;
import re;
from glob import glob;
from uuid import uuid4;
from elasticsearch import Elasticsearch;
from elasticsearch import helpers;
from operator import itemgetter;
from sparser import *;
from context import *;
from parselog import *;
import settings;


es = Elasticsearch (["elkdev1:9200"]);

def parseargv():

	parser = argparse.ArgumentParser();
	parser.add_argument("directory", help="Working directory with raw strace dumps");
	parser.add_argument("-l", "--log", help="Enable logging to terminal", action='store_true');
	parser.add_argument("-d", "--debug", help="Enable debug output to terminal", action='store_true');
	args = parser.parse_args();
	args.directory = re.sub('(\/+)$','',args.directory);
	return args;

def gettracefiles(target):

	files = glob(target+'/'+'*');
	tracelist = [];
	log("Info: Loooking for strace files in directory "+target);

	for i in files:
		trace = open(i,'r');
		line = (trace.readline()).split(' ');
		syscall = line[1].split('(')[0];
		timestamp = float(line[0]);
		tracelist.append((timestamp,syscall,i));
		trace.close;

	tracelist=sorted(tracelist, key=itemgetter(0));
	log("Info: Found "+(str(len(tracelist)))+" files");
	log("Info: First file "+str((tracelist[0])[2])+" will be processed...");
	return tracelist;

def dotrace(member,indx):

	global es;


	speccols = {};

	log("Info: processing file "+member);

	patern = re.compile(r"(?P<epoch>\d+.\d+)\s(?P<syscall>\w+)\((?P<args>.*)\)\s+\=\s(?P<rc>.*)\s\<(?P<runt>\d+.\d+)\>\n");
	pid = member.split('.')[-1];

	initlivefd(pid);
	trace = open(member,'r');

	for line in trace:

		try:
			basecols = patern.search(line).groupdict();

		except AttributeError:
			log("Error: Line \""+line[:35]+" ...\" in file "+member+" was not parsed!");
			continue;

		contextcols = {};

		basecols['pid'] = pid;
		basecols['tracefile'] = member;

		speccols = addcolumns(basecols);
		argcols = addargcols(basecols['syscall'],basecols['args']);
		rccols = addrccols(basecols['syscall'],basecols['rc']);
		contextcols = addcontextcols({**basecols, **speccols, **argcols, **rccols});

		elkdoc = {**basecols, **speccols, **argcols, **rccols, **contextcols};

		debug(elkdoc);
		debug(settings.livefd);
#		debug(settings.clonedfd);
		debug("");
		debug("");
		debug("");

#		es.index(index=indx, doc_type='trace', id=settings.iddoc, body=elkdoc);

		settings.iddoc += 1;

	trace.close;
	return 0;


def createindex(id):
	global es;
	indx =[];

	indx.append('linux.main.'+id);
	#indx[0] = ('linux.main.'+id);
	#indx[1] = ('linux.sessions.'+id);
	#indx[2] = ('linux.relations.'+id);

	try:
#		es.indices.create(index = indx[0], ignore=400);
		log('Info: Index '+indx[0]+' has been created');
	except:
		log('Error: Index '+indx[0]+' was not created!');

	return indx;


# MAIN !

settings.init();

args=parseargv();
settings.logging=False;
settings.debugging=False;

settings.logging=args.log;
settings.debugging=args.debug;
traces=gettracefiles(args.directory);
id=str(uuid4().hex)[:8];
createindex(id);
for trace in traces:
	dotrace(trace[2],'linux.main.'+id);
	#debug(settings.clonedfd);

#print(*settings.clonedfd, sep='\n');
