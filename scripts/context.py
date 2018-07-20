# context module for adding sessions to output etc

import re;
import uuid;
import settings;
from parselog import *;


def createrecord(syscallrec):

	contextcols = {};

	fd = syscallrec['r_fd'];
	starttime=syscallrec['u_epoch'];
	stoptime=[];
	pid=syscallrec['pid'];
	objectname=syscallrec['r_objectname'];
	id=str(uuid.uuid4().hex)[:8];

	settings.livefd[fd] = [pid,starttime,stoptime,objectname,id];
	contextcols['sessionid'] = id;

	return contextcols;

def mulrecord(syscallrec):

	contextcols = {};

	starttime=syscallrec['u_epoch'];
	stoptime=[];
	pid=syscallrec['pid'];
	id=str(uuid.uuid4().hex)[:8];


	fd = syscallrec['fd1'];
	objectname=syscallrec['object1'];
	settings.livefd[fd] = [pid,starttime,stoptime,objectname,id];

	fd = syscallrec['fd2'];
	objectname=syscallrec['object2'];
	settings.livefd[fd] = [pid,starttime,stoptime,objectname,id];

	#print(livefd);

	contextcols['sessionid'] = id;
	return contextcols;

def dup2record(syscallrec):

	contextcols = {};

	starttime=syscallrec['u_epoch'];
	pid=syscallrec['pid'];
	id=str(uuid.uuid4().hex)[:8];

	fd = syscallrec['n_fd'];

	try:

		settings.livefd[fd][2] = syscallrec['u_epoch'];
		del settings.livefd[fd];

	except KeyError:
		log("Info: Renewed file descriptor not found during tracking dup2 syscall");

	stoptime = "";
	fd = syscallrec['r_fd'];
	objectname=syscallrec['r_objectname'];
	settings.livefd[fd] = [pid,starttime,stoptime,objectname,id];

	#print(livefd);

	contextcols['sessionid'] = id;
	return contextcols;



def getrecord(syscallrec):

	contextcols = {};

	try:
		fd = syscallrec['fd'];
		contextcols['sessionid'] = settings.livefd[fd][4];

	except KeyError:

		log('Error: During operation getrecord session was not found for descriptor: '+syscallrec['fd']+', time: '+str(syscallrec['epoch'])+', syscall: '+syscallrec['syscall']);

	return contextcols;

def delrecord(syscallrec):

	global livefd;
	global closedfd;
	contextcols = {};

	fd = syscallrec['fd'];

	try:

		settings.livefd[fd][2] = syscallrec['u_epoch'];

	except KeyError:

		log('Error: During operation delrecord session was not found for descriptor: '+syscallrec['fd']+', time: '+str(syscallrec['epoch'])+', syscall: '+syscallrec['syscall']);
		return contextcols;


	contextcols['sessionid'] = settings.livefd[fd][4];

	settings.closedfd.append(settings.livefd[fd]+[fd]);

	del settings.livefd[fd];

	return contextcols;


def clonerecord(syscallrec):

	global livefd;
	global clonedfd;

	tempfd = {};
	contextcols = {};


	pid = syscallrec['childpid'];
	starttime = syscallrec['u_epoch'];
	stoptime = "";


	for k in settings.livefd:

		id=str(uuid.uuid4().hex)[:8];
		objectname = settings.livefd[k][3];
		tempfd[k] = [pid,starttime,stoptime,objectname,id];


	settings.clonedfd[pid] = {**tempfd};

	return contextcols;

def initlivefd(pid):

	global livefd;
	global clonefd;

	try:
		settings.livefd = {**settings.clonedfd[pid]};

	except KeyError:
		log('Info: cloned descriptors not found for pid: ');

	return 0


def addcontextcols(syscallrec):

	import cntxfnct;

	contextcols = {};
	syscall = syscallrec['syscall'];

	try:
		contextcols = cntxfnct.cntxfnct[syscall](syscallrec);

	except KeyError:
		pass

	return contextcols;


def fcntlrecord(syscallrec):

	contextcols = {};

	if not 'objectname' in syscallrec:
		return contextcols;

	objectname = syscallrec['objectname'];
	cmdargs = syscallrec['cmdargs'];
	contextcols['fcntlcmd'] = re.split(', ',cmdargs,maxsplit=1)[0];

	if contextcols['fcntlcmd'] in ('F_GETFD', 'F_GETFL'):
		fd = syscallrec['fd'];
		contextcols['sessionid'] = settings.livefd[fd][4];

	elif contextcols['fcntlcmd'] in('F_SETFD'):
		fd = syscallrec['fd'];
		contextcols['sessionid'] = settings.livefd[fd][4];
		contextcols['fcntlargs'] = re.split(', ',cmdargs,maxsplit=1)[1];

	elif contextcols['fcntlcmd'] in ('F_DUPFD', 'F_DUPFD_CLOEXEC'):

		fd = syscallrec['fd'];
		rcs = re.match('(\d+)\<(.*)\>', syscallrec['rc']).groups();
		contextcols['fcntlargs'] = re.split(', ',cmdargs,maxsplit=1)[1];

		starttime = syscallrec['u_epoch'];
		stoptime = "";
		pid = syscallrec['pid'];
		r_fd = rcs[0];
		r_objectname = rcs[1];
		r_id=str(uuid.uuid4().hex)[:8];
		settings.livefd[r_fd] = [pid,starttime,stoptime,r_objectname,r_id];

		contextcols['sessionid'] = r_id;
		contextcols['r_objectname'] = r_objectname;
		contextcols['r_fd'] = r_fd;


	return contextcols;

def mmaprecord(syscallrec):

	def mapfile(syscallrec):

		contextcols = {};

		try:
			fd = syscallrec['fd'];
			contextcols['sessionid'] = settings.livefd[fd][4];

		except KeyError:
			log('Error: During operation maprecord session was not found for descriptor: '+syscallrec['fd']+', time: '+str(syscallrec['epoch'])+', syscall: '+syscallrec['syscall']);

		return contextcols;


	def mapanonymous(syscallrec):

		contextcols = {};
		mmapargs = [];
		args = syscallrec['args'];

		mmapargs = re.split(', ',args);

		contextcols['addr'] = mmapargs[0];
		contextcols['size'] = mmapargs[1];
		contextcols['protection'] = mmapargs[2];
		contextcols['flags'] = mmapargs[3];
		contextcols['offset'] = mmapargs[5];

		return contextcols;

	contextcols = {};

	if 'objectname' in syscallrec:
		contextcols = mapfile(syscallrec);
	else:
		contextcols = mapanonymous(syscallrec);

	return contextcols
