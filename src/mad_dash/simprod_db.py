import os
from os.path import join
from pymongo import MongoClient

#f = open(join(os.environ['HOME'],'.mongo'))
#f = open(join(os.environ['MONGO'],'.mongo'))
f = open('/home/olivas/.mongo'))
url = "mongodb://DBadmin:%s@mongodb-simprod.icecube.wisc.edu" % f.readline().strip()
spdb = MongoClient(url)
