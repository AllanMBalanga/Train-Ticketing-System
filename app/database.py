from pymongo import MongoClient
from .config import settings
#"mongodb://<username>:<password>@localhost:27017/"
client = MongoClient(f"mongodb://{settings.database_user}:{settings.database_password}@{settings.database_host}:27017/?authSource=admin")

#create an instance of database trains
db = client.trains

#database tables
users = db.users
balances = db.balances
transactions = db.transactions
trains = db.trains
stations = db.stations
travels = db.travels
payments = db.payments