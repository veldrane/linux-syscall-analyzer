import re;


argregex = {
	"open" :        '(?P<request>.*)\"\,\s(?P<mode>.*)',
	"close" :       '(?P<fd>\d+)\<(?P<objectname>.*)\>',
	"listen" :       '(?P<fd>\d+)\<(?P<objectname>.*)\>,\s(?P<backlog>\d+)',
	"bind" :		'(?P<fd>\d+)\<(?P<objectname>.*)\>\,\s\{(?P<sockaddr>.*)\}.*',
	"accept" :		'(?P<r_fd>\d+)\<(?P<r_objectname>.*)\>\,\s\{(?P<sockaddr>.*)\}.*',
	"dup" :	        '(?P<r_fd>\d+)\<(?P<r_objectname>.*)\>',
	"dup2" :	    '(?P<r_fd>\d+)\<(?P<r_objectname>.*)\>\,\s(?P<n_fd>\d+)\<(?P<c_objectname>.*)\>',
	"dup3" :	    '(?P<r_fd>\d+)\<(?P<r_objectname>.*)\>\,\s(?P<n_fd>\d+)\<(?P<c_objectname>.*)\>\,(?P<flags>.*)',
	"mmap" :        '(?P<addr>.*)\,\s(?P<size>\d+)\,\s(?P<protection>.*)\,\s(?P<flags>.*)\,\s(?P<fd>.*).*\,\s(?P<offset>.*)',
	"read" :        '(?P<fd>\d+)\<(?P<objectname>.*)\>\,\s(?P<data>.*)\,\s(?P<size>\d+)',
	"write" :       '(?P<fd>\d+).*\,\s(?P<data>.*)\,\s(?P<size>\d+)',
	"fcntl" :       '(?P<fd>\d+)\<(?P<objectname>.*)\>\,\s(?P<cmd>.*)',
	"socket" :      '(?P<domain>.*)\,\s(?P<type>.*)\,\s(?P<protocol>.*)',
	"execve" :      '\"(?P<command>.*)\"\,\s\[(?P<options>.*)\]\,\s(.*)\]'

	}

rcregex = {
	"open" :        '(?P<fd>\d+)\<(?P<objectname>.*)\>',
	"accept" :      '(?P<fd>\d+)\<(?P<objectname>.*)\>',
	"socket" :      '(?P<fd>\d+)\<(?P<objectname>.*)\>',
	"dup" :			'(?P<fd>\d+)\<(?P<objectname>.*)\>',
	"dup2" :		'(?P<fd>\d+)\<(?P<objectname>.*)\>',
	"dup3" :		'(?P<fd>\d+)\<(?P<objectname>.*)\>',
	"clone" :       '(?P<childpid>\d+)'
}


def addargcols(syscall,args):

	global argregex;

	try:
		argpatern = re.compile(argregex[syscall]);
		parsed = argpatern.search(args).groupdict();
	except:
		parsed = {};

	return parsed;


def addrccols(syscall,rc):

	global rcregex;

	try:
		argpatern = re.compile(rcregex[syscall]);
		parsed = argpatern.search(rc).groupdict();
	except:
		parsed = {};

	return parsed;
