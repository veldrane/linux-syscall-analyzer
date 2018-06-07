import argparse;
import re;
import glob;
import uuid;
from elasticsearch import Elasticsearch;
from elasticsearch import helpers;
from operator import itemgetter;
import datetime;
import time;
from sparser import *;
import context;


VERSION = "0.1";
logging = False;
es = Elasticsearch (["elkdev1:9200"]);
iddoc=1;

livefd = {};
closedfd=[];



contextf = {
	"open" : context.c_open,
	"read" : context.c_read,
	"write" : context.c_write
}

def createrecord(syscallrec):

	global livefd;
	contextcols = {};

	fd = syscallrec['r_fd'];
	starttime=syscallrec['u_epoch'];
	stoptime=[];
	pid=syscallrec['pid'];
	objectname=syscallrec['r_objectname'];
	id=str(uuid.uuid4().hex)[:8];

	livefd[fd] = [pid,starttime,stoptime,objectname,id];
	contextcols['sessionid'] = id;

	return contextcols;

def mulrecord(syscallrec):

	global livefd;
	contextcols = {};

	starttime=syscallrec['u_epoch'];
	stoptime=[];
	pid=syscallrec['pid'];
	id=str(uuid.uuid4().hex)[:8];


	fd = syscallrec['fd1'];
	objectname=syscallrec['object1'];
	livefd[fd] = [pid,starttime,stoptime,objectname,id];

	fd = syscallrec['fd2'];
	objectname=syscallrec['object2'];
	livefd[fd] = [pid,starttime,stoptime,objectname,id];

	#print(livefd);

	contextcols['sessionid'] = id;
	return contextcols;


def getrecord(syscallrec):

	global livefd;
	contextcols = {};

	fd = syscallrec['fd'];
	contextcols['sessionid'] = livefd[fd][4];

	return contextcols;

def delrecord(syscallrec):

	global livefd;
	global closedfd;
	contextcols = {};

	fd = syscallrec['fd'];
	livefd[fd][2] = syscallrec['u_epoch'];

	contextcols['sessionid'] = livefd[fd][4];

	closedfd.append(livefd[fd]+[fd]);

	del livefd[fd];

	return contextcols;


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

def dotrace(member,indx):

	global es;
	global iddoc;
	global closedfd;

	crlist = ('open','openat','socket','accept');
	modlist = ('read', 'write','rcvfrom','sendto','accept','bind','fcntl','getdents');
	dellist = {'close'};
	mullist = {'pipe','socketpair'};
	clonelist={'clone'};

	speccols = {};

	patern = re.compile(r"(?P<epoch>\d+.\d+)\s(?P<syscall>\w+)\((?P<args>.*)\)\s+\=\s(?P<rc>.*)\s\<(?P<runt>\d+.\d+)\>\n");
	pid = member.split('.')[-1];
	trace = open(member,'r');

	for line in trace:

		try:
			basecols = patern.search(line).groupdict();

		except AttributeError:
			log("Error: Line \""+line[:35]+" ...\" in file "+member+" was not parsed!");
			continue;


		basecols['pid'] = pid;
		basecols['tracefile'] = member;

		speccols = addcolumns(basecols);
		argcols = addargcols(basecols['syscall'],basecols['args']);
		rccols = addrccols(basecols['syscall'],basecols['rc']);

		contextcols = {};

		if (basecols['syscall'] in dellist) and ('fd' in argcols):

			contextcols = delrecord({**basecols, **speccols, **argcols, **rccols});

		if (basecols['syscall'] in crlist) and ('r_fd' in rccols):

			contextcols = createrecord({**basecols, **speccols, **argcols, **rccols});

		if (basecols['syscall'] in mullist):

			contextcols = mulrecord({**basecols, **speccols, **argcols, **rccols});

		if (basecols['syscall'] in modlist) and ('fd' in argcols) and (argcols['fd']  != "-1"):

			#print({**basecols, **speccols, **argcols, **rccols});
			contextcols = getrecord({**basecols, **speccols, **argcols, **rccols});


		elkdoc = {**basecols, **speccols, **argcols, **rccols, **contextcols};
		#print(elkdoc);

		#print(livefd);



		#es.index(index=indx, doc_type='trace', id=iddoc, body=elkdoc);
		iddoc += 1;

	trace.close;
	return 0;

def addcolumns(basecols):

	speccols = {};

	speccols['runt'] = float(basecols['runt']);
	speccols['epoch'] = float(basecols['epoch']);

	speccols['u_epoch'] = int(speccols['epoch']*1000000);
	speccols['u_runt'] = int(speccols['runt']*1000000);
	speccols['@timestamp'] = datetime.datetime.fromtimestamp(speccols['epoch']).strftime('%Y-%m-%dT%H:%M:%S.%fZ');

	return speccols;



def createindex(id):
	global es;
	indx =[];

	indx.append('linux.main.'+id);
	#indx[0] = ('linux.main.'+id);
	#indx[1] = ('linux.sessions.'+id);
	#indx[2] = ('linux.relations.'+id);

	try:
	#	es.indices.create(index = indx[0], ignore=400);
		log('Index '+indx[0]+' has been created');
	except:
		log('Index '+indx[0]+' was not created');

	return indx;


args=parseargv();
logging=args.log
traces=gettracefiles(args.directory);
id=str(uuid.uuid4().hex)[:8];
createindex(id);
for trace in traces:
	dotrace(trace[2],'linux.main.'+id);

print(*closedfd, sep='\n');
