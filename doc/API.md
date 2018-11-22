### General ###

After parsing and processing the data, elkpump create thousands and thousands documents in elasticsearch or just (in the future) one big
CSV. One syscall row in the trace means one doc in elasticsearch. Columns have been unsualy named based on their definitian in the 
syscall(2) man page. Because duplication ocured i tried to distuinguis between arguments value and return (return values have r_ prfiex).
Parsing is proceed in three main phases:
	
	- elkpump.py -> function do_trace() -> variable pattern
		- this is the base parsing of the syscall itself. Program get the info about the time of running, syscall, raw arguments
		  and raw return code

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
the kibana or elasticsearch.

### API ###



		  

