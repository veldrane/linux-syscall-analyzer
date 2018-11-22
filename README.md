# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

##### Quick summary #####

Toolset for the syscall analysis of the linux binary, it tries parsing strace logs, store them in elasticsearch db
and open them for further analysis. Some kibana dashboards are attached as well. The main tool elkpump.py is writen in
python. Main goal is the aggregation of some syscalls (at the momemnt related to fd) via unique id to groups and open them for 
analysis based on their lifecycle, transfered data, etc. Elkmpump tracks the filedescriptor from the beginning to the end, knows not 
only open syscall but dup, dup2, duplication via fcntl, via clone syscall etc. Only creation via messages is not supported
yet. When a fd is born, sessionid is assigned and all related syscalls are marked with the same id. If the fd
is inherit via clone syscall, new sessionid is created. At the moment no collision detection is implemented against the 
sessionid :). Elkpump support also internal processing of some syscalls, their diferent behaviour in some cases (for example
mmap: anonymous vs file maped), map some usefull information to integer of float before the ending to the backend. Toolset 
could be really usefull for:

 - Revealing internal architecture of the application from the linux point of view
 - Building tight security policies
 - Visualising data flows inside the traced application
 - Getting the status of the application in certain point of the time from the os prospective
 - Application resource analysis

 ... and so on.

	
Elkpump means elasticsearch pump what is meaningless so in some future time will be renamed :).


	
##### Version #####
	
0.00001b :)

	
### How do I get set up? ###


##### Repository info: #####

./kibana:
 - export of some kibana search, visualisation and the dashboards

./logstash:
 - old version based on the logstash - deprecated

./scripts:
 - main program (elkpump.py) + modules. No package here - sorry :)

./test:
 - some test data and templates for the syscalls
  ./test/raw:
 - strace export of running sshd - usefull for initial testing

./doc:
- some documentation


##### Summary of set up #####

Following packages should be installed:
 - server side (database backend):
    elasticsearch-6.2.3-1.noarch
    kibana-6.2.3-1.x86_64

 - client side (elkpump.py script):
    python3
    modules: argparse, re, uuid, glob, copy, Elasticsearch, itemgetter, csv (is not used)
	  
 - strace requirements:
    tested version: 4.12 (lower version can have a problem with missing information in some syscalls)


##### Elasticsearch Configuration #####

Elasticsearch database must be visible via tcp ip.	


##### Strace configuration #####

Traces must be captured in certain format:

    strace -y -T -ttt -ff -x -qq -o <FILE_PREFIX> <COMMAND>
	
Examples:

    [oracle@oradb1 ~]$ export COMMAND='sqlplus / as sysdba'
    [oracle@oradb1 ~]$ strace -y -T -ttt -ff -x -qq -o sqlplus $COMMAND

After start second command strace start writing traces to current directory for current process and all childs. 


### Run elkpump ###

	$ python elkpump.py elk -h
	usage: elkpump elk [-h] [-s SERVER] [-b BUFFER] [-i INDEX]

	optional arguments:
  	-h, --help            	show this help message and exit
  	-s SERVER, --server SERVER
                        	Elastic search server destination, default connection:
                        	localhost:9200
  	-b BUFFER, --buffer BUFFER
                        	Number of docs for bulk post, default: 10000
  	-i INDEX, --index INDEX
                        	Index name, default: linux.main.<random_id>

	Example:

	python elkpump.py elk --server elkdev1:9200 /data/tests/oracle -l
	
elkpump will start and process all logs in /data/tests/oracle, produce logging and store all data on the server elkdev1:9200
CSV subcommand is not supported yet.

    $ python elkpump.py elk --server elkdev1:9200 /data/tests/oracle -l
    Thu Nov 22 17:30:55 2018 ---| Info: Loooking for strace files in directory /data/tests/oracle
    Thu Nov 22 17:30:55 2018 ---| Info: Found 655 files
    Thu Nov 22 17:30:55 2018 ---| Info: First file /data/tests/oracle/sqlplus.2620 will be processed...
    Thu Nov 22 17:30:56 2018 ---| Info: Index <pre>linux.main.f82a63d7</pre> has been created
    Thu Nov 22 17:30:56 2018 ---| Info: processing file /data/tests/oracle/sqlplus.2620
    Thu Nov 22 17:30:56 2018 ---| Info: cloned descriptors not found for pid: 
    Thu Nov 22 17:30:56 2018 ---| Warning: During operation getrecord session was not found for descriptor: 1, time: 1533726043.017823, syscall: write
    Thu Nov 22 17:30:56 2018 ---| Warning: During operation getrecord session was not found for descriptor: 1, time: 1533726043.018125, syscall: write
    Thu Nov 22 17:30:56 2018 ---| Warning: During operation getrecord session was not found for descriptor: 1, time: 1533726043.018251, syscall: write
    ...
    ...

After finish of the elkpump.py you can check the status of new created index in elasticsearch

    $ curl http://elkdev1:9200/_cat/indices?v
    health status index               uuid                   pri rep docs.count docs.deleted store.size pri.store.size
    green  open   .kibana             yr45Pp9dRwWzDms0hsWc1A   1   0         23            1     43.2kb         43.2kb
    yellow open   linux.main.d4c48ea0 TFMdrRYNQMGg-gaiUhfytg   5   1    1754821            0      284mb          284mb
    yellow open   linux.main.1c2e1767 BVncpzmwRburCDQqRYYwaA   5   1     835858            0    136.6mb        136.6mb
    yellow open   ```linux.main.f82a63d7``` zp-QDG1XSVeWCX3OauTFKA   5   1    1760508            0      288mb          288mb



### Usual workflow ###

- run strace on the analyzed application and store the output (prepare fs for posible huge amount of data)
- run elasticsearch and kibana
- run elkpump agains the trace output and elkserver
- login to kibana and register index.
- optional: load the dashboards from ./kibana directory and pair them with the index
- analyze what ever you want.

### Limitation and BUGS ###
	
- elkpump doesn't support strace output from attaching pid. Supported is just running application for the beginning to the 
  end. Tool probably does own job, but was not tested under this circumstances
- elkpump doesn't support https connection with elasticsearch server
- elkpump doesn't check duplication sessionid so it's a little chance that two same sessionid can be generated
- elkpump doesn't support the message fd creation (ehm systemd :))
- csv is not supported yet (plan for the near future version)
- some syscalls variation is not probably supported (for example read, pread, read64 etc - these are supported but
  there is a huge list of them. Adding similar syscalls is not rocket science - please check sparser.py and argregex array)
- elasticsearch doesn't support microsecond precision yet.

### Future ###
	
- Extend documentation of the all columns of output documents - see the doc/ directory
- Full CSV format support
- Appropriate .r files for analysing csv in R	
- Adding more dashboards, visualisation and search to the Kibana.
- Full memory allocation and dealocation support to elkpump (feasible ?)
- Better thread and process spawn (contexting clone, exec, fork etc)
- Adding support for signal familly syscalls 
- Support for strace attach pid functionality (not so important)
- Describe in detail as much syscalls as possible
