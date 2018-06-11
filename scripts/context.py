# context module for adding sessions to output etc

import uuid;
import settings;


crlist = ('open','openat','socket','accept');
modlist = ('read', 'write','rcvfrom','sendto','accept','bind','fcntl','getdents');
dellist = {'close'};
mullist = {'pipe','socketpair'};
clonelist={'clone'};




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


def getrecord(syscallrec):

	contextcols = {};

	fd = syscallrec['fd'];
	contextcols['sessionid'] = settings.livefd[fd][4];

	return contextcols;

def delrecord(syscallrec):

	global livefd;
	global closedfd;
	contextcols = {};

	fd = syscallrec['fd'];
	settings.livefd[fd][2] = syscallrec['u_epoch'];

	contextcols['sessionid'] = settings.livefd[fd][4];

	settings.closedfd.append(settings.livefd[fd]+[fd]);

	del settings.livefd[fd];

	return contextcols;


def clonerecord(syscallrec):

	global livefd;
	global clonedfd;

	pid = syscallrec['childpid'];

	settings.clonedfd[pid] = settings.livefd;

	return;



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

    return contextcols;
