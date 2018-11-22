### General ###

After parsing and processing the data, elkpump create thousands and thousands documents in elasticsearch or just (in the future) one big
CSV. One syscall row in the trace means one doc in elasticsearch. Columns have been unsualy named based on their definitian in the 
syscall(2) man page. Because duplication ocured i tried to distuinguis between arguments value and return (return values have r_ prfiex).
Parsing is done in four main phases: base parsing of the whole syscall line, parsing of the arguments, return code, and finaly adding
context keys and taking into consideration special behaviour of some syscalls.
	
> - elkpump.py -> function do_trace() -> variable pattern
>   this is the base parsing of the syscall itself. Program get the info about the time of running, syscall, raw arguments
>   and raw return code

- sparser.py -> array argregex 
  after base parsing, program get the syscall name a try to parse arguments in more detail way. It tries to find apropriate 
  value for key in argregex and if the value is foundi, additional keys and values are created by applaing regex to raw 
  arguments line.

- sparser.py -> array rcregex
  the same process like before is applied to raw return code.

- cntxfnct.py -> array cntxfnct
  for the special syscalls the context or additional informations are attached. For this purpose each syscall listed in the
  array is processed via the procedure listed like a key in the array. In this step sessionid or special keys are added 
  to the output doc. For example: if the open syscall is processed new sessionid is created. If the mmap syscall is processed
  it has to decided if the mmap just allocate anonymouse memory block or it's related to some fd and must be markded with the 
  sessionid.

The following keys can be used for the analysis like a result of the process described above. Based on them you can create searches in 
the kibana or elasticsearch. Not all keys are described here, if you are interested in please have a look to the syscall(2) man pages
for appropriate variables

### Fields description ###


##### epoch (type time), u_epoch (type int) ######

Start of the each syscall in unix time with microseconds precision. This key is mapped to elasticsearch datetime array. Unfortunatelly 
elasticsearch itself doesnt have support for microseconds so last 3 digits are cutted (see BUGS and LIMITATION in readme file), for this
purpose u_runt is created and it is stored like a usual integer.


##### syscall (type str) ######

Key describe syscall name

##### args (type str) ######

Raw arguments line

##### rc (type str) ######

Raw return code line

##### runt (type float) u_runt(type int) ######

Time spent in the syscall itself, urunt is derived from runt multiplaing by 1000000 (time in miliseconds - more readable)

##### size (type int) ######

Some syscalls provide information about size of the object. For example write or read reports how many bytes were transfered etc.
This key is valuable when you need to know amount of transfered data etc

##### offset (type str) ######

Information about the offset in specified object (mmap syscall, seek etc)

##### objectname, r_objectname, n_objectname (type str) #####

Information about object in arguments of the syscall. It can be filename, socketname, pipe etc.)Its a usefull if you are looking
for per file statistics etc .R_objectname is the same but for the return code (some sycalls have object in arguments and return code).
For example: it is valuable for detecting simlink acess as well, because in this case the objectname and r_objectname are different.

n_objectname is used for new object creation from current (dup, dup2, dup3 syscall). Probably will be deprecated in the near future

##### sessionid (type str) ######

When the fd is created, sessionid is generated assigned to output doc and stored in the internal structure. For the next syscall 
manipulate with certain fd, elkpump tries to search this sessionid based on the fd number and pid. If the keys is found, output 
document with the syscall is marked with the same string. After close syscall sessionid is deleted from internal structure, so 
the same or different file opened in other point of time have a different id and are distuinguish with each other. All syscalls 
realated to one sessionid is can be marked like one "session". During the analysis in kibana or any other tool you are able to
found how many times the file has been opened, how much data have been transfered via one session or as whole etc etc, so you can
quickly find information about data flow, time spent by fd operation, architecture etc. It does worth to mention that sessionid
is not created just in case of fileopen but socket are supported as well. On the other hand not all syscalls are suppored yet.

