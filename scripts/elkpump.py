# MAIN program
import argparse;
import re;
import csv;
import json;
from glob import glob;
from uuid import uuid4;
from copy import copy;
from elasticsearch import Elasticsearch;
from operator import itemgetter;


from sparser import *;
from context import *;
from parselog import *;
import settings;


bulkdata = [];
outputcsv = None;

def initglobals(args):

	if args.server: settings.elkserver = args.server;
	if args.log: settings.logging = args.log;
	if args.debug: settings.debugging = args.debug;

	return 0;

def parseargv():

	parser = argparse.ArgumentParser(prog='elkpump', description='elkpump is the tool for parsing and adding context strace output');
	subparsers = parser.add_subparsers(help='sub-command help', dest='destination');

	parser_elk = subparsers.add_parser('elk', help='elk help');
	parser_elk.add_argument('-s','--server', help='Elastic search server destination, default connection: localhost:9200');
	parser_elk.add_argument('-b','--buffer', help='Number of docs for bulk post, default: 10000');
	parser_elk.add_argument('-i','--index', help='Index name, default: linux.main.<random_id>');

	parser_csv = subparsers.add_parser('csv', help='csv help');
	parser_csv.add_argument('-c','--csvfile', help='CSV out file, default file: output.csv');

	parser_json = subparsers.add_parser('json', help='json help');
	parser_json.add_argument('-c','--jsonfile', help='json out file, default file: output.json');


#	parser.add_argument("destination", help="Output destination");
	parser.add_argument("directory", help="Working directory with raw strace dumps");
	parser.add_argument("-l", "--log", help="Enable logging to terminal", action='store_true');
	parser.add_argument("-d", "--debug", help="Enable debug output to terminal", action='store_true');

	args = parser.parse_args();
	args.directory = re.sub('(\/+)$','',args.directory);
	return args;

def pushtoelk(elkdoc):

	global bulkdata;
	global es;
	bulkheader = {};

	bulkheader['index'] = {"_index": settings.esindx, "_type" : 'trace', "_id" : settings.iddoc};
	bulkid = ((settings.iddoc + settings.numdocs)%settings.numdocs);
	bulkdata.append(copy(bulkheader));
	bulkdata.append(copy(elkdoc));

	if (bulkid%settings.numdocs) == 0:

		rs = es.bulk(index = settings.esindx, body = bulkdata,refresh = True);
		bulkdata = [];

	return 0;

def flushelk():

	global bulkdata;
	global es;
	rs = es.bulk(index = settings.esindx, body = bulkdata,refresh = True);
	bulkdata = [];

	return 0

def createcsv():

	global outputcsv;

	csvheader = ['epoch','syscall','args','rc','runt']
	if settings.csvfile:
		csvfile = settings.csvfile;
	else:
		csvfile = "output.csv";

	outputcsv = open(csvfile,'w');
	writer = csv.DictWriter(outputcsv,fieldnames = csvheader);
	writer.writeheader();

	return outputcsv;

def pushtocsv(elkdoc):

	global bulkdata;
	global outputcsv;

	tempdata=[elkdoc['epoch'],elkdoc['syscall'],elkdoc['args'],elkdoc['rc'],elkdoc['runt']];

	bulkheader = {};

	bulkid = ((settings.iddoc + settings.numdocs)%settings.numdocs);
	bulkdata.append(copy(tempdata));

	if (bulkid%settings.numdocs) == 0:

		writer = csv.DictWriter(outputcsv,fieldnames = bulkdata);
		writer.writerows();

	return 0;

def createjson():

	global outputjson;

	if settings.jsonfile:
		jsonfile = settings.jsonfile;
	else:
		jsonfile = "output.json";

	outputjson = open(jsonfile,'w');

	return outputjson;


def pushtojson(elkdoc):

	global outputjson;

	elkdoc['args'] = re.sub(r'\{|\}','',elkdoc['args'])

	if (settings.iddoc) == 1:
		json.dump(elkdoc, outputjson);
		return 0
	else:
		pass
	outputjson.write("\n")
#	outputjson.write(',');
	json.dump(elkdoc, outputjson);

	return 0;


def gettracefiles(target):

	files = glob(target+'/'+'*');
	tracelist = [];
	log("Info: Loooking for strace files in directory "+target);

	for i in files:
		trace = open(i,'r');
		line = (trace.readline()).split(' ');
		syscall = line[1].split('(')[0];
		timestamp = float(line[0]);
		tracelist.append((timestamp,syscall,i));
		trace.close;

	tracelist=sorted(tracelist, key=itemgetter(0));
	log("Info: Found "+(str(len(tracelist)))+" files");
	log("Info: First file "+str((tracelist[0])[2])+" will be processed...");
	return tracelist;

def dotrace(member):

	global es;

	speccols = {};
	testid = settings.iddoc;

	log("Info: processing file "+member);

	patern = re.compile(r"(?P<epoch>\d+.\d+)\s(?P<syscall>\w+)\((?P<args>.*)\)\s+\=\s(?P<rc>.*)\s\<(?P<runt>\d+.\d+)\>\n");
	pid = member.split('.')[-1];

	initlivefd(pid);
	trace = open(member,'r');

	for line in trace:

		try:
			basecols = patern.search(line).groupdict();

		except AttributeError:
			log("Warning: Line \""+line[:35]+" ...\" in file "+member+" was not parsed!");
			continue;

		contextcols = {};

		basecols['pid'] = pid;
		basecols['tracefile'] = member;

		speccols = addcolumns(basecols);
		argcols = addargcols(basecols['syscall'],basecols['args']);
		rccols = addrccols(basecols['syscall'],basecols['rc']);
		contextcols = addcontextcols({**basecols, **speccols, **argcols, **rccols});

		elkdoc = {**basecols, **speccols, **argcols, **rccols, **contextcols};
		debug(elkdoc);
		pushtoelk(elkdoc);
#		pushtojson(elkdoc)
#		pushtocsv(elkdoc);
		settings.iddoc += 1;

	#	es.index(index=indx, doc_type='trace', id=settings.iddoc, body=elkdoc);

	flushelk();
	trace.close;
	return 0;

def createindex(id):
	global es;
	indx =[];

	indx.append('linux.main.'+id);
	#indx[0] = ('linux.main.'+id);
	#indx[1] = ('linux.sessions.'+id);
	#indx[2] = ('linux.relations.'+id);

	try:
		rc = es.indices.create(index = indx[0], ignore=400);
		log('Info: Index '+indx[0]+' has been created');
	except:
		log('Error: Index '+indx[0]+' was not created!');
		exit(1);

	return indx[0];

###############
####### MAIN !

settings.init();
args=parseargv();
initglobals(args);

es = Elasticsearch([settings.elkserver]);
if not es.ping():
    raise ValueError("Connection failed")

traces=gettracefiles(args.directory);
id=str(uuid4().hex)[:8];
settings.esindx = createindex(id);
#output = createjson();
for trace in traces:
	dotrace(trace[2]);
	#debug(settings.clonedfd);

#outputjson.close();

#print(*settings.clonedfd, sep='\n');
