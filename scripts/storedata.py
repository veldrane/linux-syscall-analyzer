import settings;
from parslog import *;
from elasticsearch import Elasticsearch;

es = Elasticsearch (["elkdev1:9200"]);


def pushtoelk(elkdoc):

    global es;
    bulkdata = [];
    bulkheader = {};


    bulkheader['index'] ={"_index": elkdoc['index'], "_type" : 'trace', "_id" : settings.iddoc};


    bulkid = ((settings.iddoc + settings.numdocs)%settings.numdocs);
    settings.bulkdata.append(copy(bulkheader));
    settings.bulkdata.append(copy(elkdoc));

    if (bulkid%settings.numdocs) == 0:

      rs = es.bulk(index = indx, body = bulkdata,refresh = True);
      bulkdata = [];

return 0;
