from pymongo import MongoClient

#"mongodb://<username>:<password>@localhost:27017/"
client = MongoClient("mongodb://admin:031802@localhost:27017/?authSource=admin")

#create an instance of database trains
db = client.trains