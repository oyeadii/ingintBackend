import pymongo

class MongoDbConnections:
    def __init__(self,url,dbName):
        if not url or not dbName:
            raise Exception(11009)
        client = pymongo.MongoClient(url)
        self.database = client[dbName]
         
    def get_collection(self,collName):
        self.collection = self.database[collName]
        return self.collection
