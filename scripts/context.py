# context module for adding sessions to output etc

import uuid;
import settings;


crlist = ('open','openat','socket','accept','dup');
modlist = ('read', 'write','rcvfrom','sendto','accept','bind','fcntl','getdents');
dellist = ('close');
mullist = ('pipe','pipe2','socketpair');
clonelist=('clone');
dup2list = ('dup2','dup3');




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
		print("Info: Renewed file descriptor not found during tracking dup2 syscall");

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

		print('Session was not found for descriptor: '+fd);

	return contextcols;

def delrecord(syscallrec):

	global livefd;
	global closedfd;
	contextcols = {};

	fd = syscallrec['fd'];

	try:

		settings.livefd[fd][2] = syscallrec['u_epoch'];

	except KeyError:

		print('Session was not found for descriptor: '+fd);
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
		print("Info: cloned descriptors not found for pid: "+pid);

	return 0


def addcontextcols(syscallrec):

	contextcols = {};

	if (syscallrec['syscall'] in dellist) and ('fd' in syscallrec):
		contextcols = delrecord(syscallrec);

	if (syscallrec['syscall'] in crlist) and ('r_fd' in syscallrec):
		contextcols = createrecord(syscallrec);

	if (syscallrec['syscall'] in mullist):
		contextcols = mulrecord(syscallrec);

	if (syscallrec['syscall'] in modlist) and ('fd' in syscallrec) and (syscallrec['fd']  != "-1"):
		contextcols = getrecord(syscallrec);

	if (syscallrec['syscall'] in clonelist):
		contextcols = clonerecord(syscallrec);

	if (syscallrec['syscall'] in dup2list):
		contextcols = dup2record(syscallrec);


	return contextcols;
