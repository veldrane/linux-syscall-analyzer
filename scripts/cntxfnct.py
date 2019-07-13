from context import *;

global cntxfnct;

cntxfnct = {
"open"			:	createrecord,
"openat"		:	createrecord,
"socket"		:	createrecord,
"accept"		:	createrecord,
"dup"			:	createrecord,
"read"			:	getrecord,
"pread64"		:	getrecord,
"write"			:	getrecord,
"pwrite64"		:	getrecord,
"rcvfrom"		:	getrecord,
"accept"		:	getrecord,
"bind"			:	getrecord,
"getdents"		:	getrecord,
"fcntl"			:	fcntlrecord,
"close"			:	delrecord,
"pipe"			:	mulrecord,
"pipe2"			:	mulrecord,
"socketpair"	:	mulrecord,
"clone"			:	clonerecord,
"dup2"			:	dup2record,
"dup3"			:	dup2record,
"mmap"			:	mmaprecord
}
