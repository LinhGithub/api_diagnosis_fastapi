from pymongo import MongoClient
import settings
from collections import OrderedDict
import sys
print(sys.argv)

def mongo_create():
    mongodb = MongoClient(
        settings.MONGODB_HOST,
        settings.MONGODB_PORT,
        # document_class=OrderedDict,
        maxPoolSize=200,
        serverSelectionTimeoutMS=90000)

    mydb = mongodb[settings.MONGODB_NAME]
    return mydb
