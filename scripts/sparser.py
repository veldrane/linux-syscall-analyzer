#sparser - module for parsing the strace messages

import re;
import datetime;

argregex = {
	"open" :        '\"(?P<objectname>.*)\"\,\s(?P<mode>.*)',
	"openat" :      '(?P<dirfd>.*)\,\s\"(?P<objectname>.*)\"\,\s(?P<mode>.*)',
	"close" :       '(?P<fd>\d+)\<(?P<objectname>.*)\>',
	"pipe" :        '(?P<fd1>\d+)\<(?P<object1>.*)\>,\s(?P<fd2>\d+)\<(?P<object2>.*)\>',
	"pipe2" :        '(?P<fd1>\d+)\<(?P<object1>.*)\>,\s(?P<fd2>\d+)\<(?P<object2>.*)\>',
	"listen" :      '(?P<fd>\d+)\<(?P<objectname>.*)\>,\s(?P<backlog>\d+)',
	"bind" :		'(?P<fd>\d+)\<(?P<objectname>.*)\>\,\s\{(?P<sockaddr>.*)\}.*',
	"accept" :		'(?P<fd>\d+)\<(?P<objectname>.*)\>\,\s\{(?P<sockaddr>.*)\}.*',
	"connect" :		'(?P<fd>\d+)\<(?P<objectname>.*)\>\,\s\{(?P<sockaddr>.*)\}.*',
	"dup" :	        '(?P<fd>\d+)\<(?P<objectname>.*)\>',
#	"dup2" :	    '(?P<fd>\d+)\<(?P<objectname>.*)\>\,\s(?P<n_fd>\d+)\<(?P<n_objectname>.*)\>',
	"dup2" :	    '(?P<fd>\d+)\<(?P<objectname>.*)\>\,\s(?P<n_fd>\d+).*',
	"dup3" :	    '(?P<fd>\d+)\<(?P<objectname>.*)\>\,\s(?P<n_fd>\d+)\<(?P<n_objectname>.*)\>\,(?P<flags>.*)',
	"mmap" :        '(?P<addr>.*)\,\s(?P<size>\d+)\,\s(?P<protection>.*)\,\s(?P<flags>.*)\,\s(?P<fd>.*)\<(?P<objectname>.*)\>\,\s(?P<offset>.*)',
#	"mmap" :        '(?P<addr>.*)\,\s(?P<size>\d+)\,\s(?P<protection>.*)\,\s(?P<flags>.*)\,\s(?P<fd>.*).*\,\s(?P<offset>.*)',
	"read" :        '(?P<fd>\d+)\<(?P<objectname>.*)\>\,\s(?P<data>.*)\,\s(?P<size>\d+)',
	"write" :       '(?P<fd>\d+).*\,\s(?P<data>.*)\,\s(?P<size>\d+)',
	"fcntl" :       '(?P<fd>\d+)\<(?P<objectname>.*)\>\,\s(?P<cmdargs>.*)',
	"socket" :      '(?P<domain>.*)\,\s(?P<type>.*)\,\s(?P<protocol>.*)',
#	"socketpair" :  '(?P<domain>.*)\,\s(?P<type>.*)\,\s(?P<protocol>.*)\,\s\[(?P<fd1>\d+)\<(?P<object1>.*)\>\,\s(?P<fd2>\d+)\<(?P<object2>.*)\>\]\>',
	"socketpair" :  '(?P<domain>[A-Z]+.[A-Z]+)\,\s(?P<type>[A-Z]+.[A-Z]+)\,\s.\,\s\[(?P<fd1>\d+)\<(?P<object1>.*)\>,\s(?P<fd2>\d+)\<(?P<object2>.*)\>\]',
	"execve" :      '\"(?P<command>.*)\"\,\s\[(?P<options>.*)\]\,\s(.*)\]',
	"getdents" :	'(?P<fd>\d+)\<(?P<objectname>.*)\>\,\s(?P<data>.*)\,\s(?P<size>\d+)'
	}

rcregex = {
	"open" :        '(?P<r_fd>\d+)\<(?P<r_objectname>.*)\>',
	"openat" :      '(?P<r_fd>\d+)\<(?P<r_objectname>.*)\>',
	"accept" :      '(?P<r_fd>\d+)\<(?P<r_objectname>.*)\>',
	"socket" :      '(?P<r_fd>\d+)\<(?P<r_objectname>.*)\>',
	"dup2" :		'(?P<r_fd>\d+)\<(?P<r_objectname>.*)\>',
	"dup" :			'(?P<r_fd>\d+)\<(?P<r_objectname>.*)\>',
	"dup3" :		'(?P<r_fd>\d+)\<(?P<r_objectname>.*)\>',
	"clone" :       '(?P<childpid>\d+)'
}


def addcolumns(basecols):

	speccols = {};

	speccols['runt'] = float(basecols['runt']);
	speccols['epoch'] = float(basecols['epoch']);

	speccols['u_epoch'] = int(speccols['epoch']*1000000);
	speccols['u_runt'] = int(speccols['runt']*1000000);
	speccols['@timestamp'] = datetime.datetime.fromtimestamp(speccols['epoch']).strftime('%Y-%m-%dT%H:%M:%S.%fZ');

	return speccols;


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
