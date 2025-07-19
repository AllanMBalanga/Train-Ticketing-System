from .database import users, balances, transactions, trains, stations, travels, payments

#Users.py
def users_find_one(user_id: int):
    return users.find_one({"user_id": user_id, "is_deleted": False})

def users_update_one(user_id: int, data: dict):
    return users.update_one({"user_id": user_id}, {"$set": data})

def users_delete_one(user_id: int):
    return users.delete_one({"user_id": user_id})

def transactions_update_many(user_id: int, data: dict):
    return transactions.update_many({"user_id": user_id}, {"$set": data})

def transactions_delete_many(user_id: int):
    return transactions.delete_many({"user_id": user_id})


#Balances.py
def balances_find_one(user_id: int, balance_id: int = None):
    if balance_id:
        return balances.find_one({"user_id": user_id, "balance_id": balance_id, "is_deleted": False})
    else:
        return balances.find_one({"user_id": user_id, "is_deleted": False})

def balances_update_one(user_id: int, data: dict, balance_id: int = None):
    if balance_id:
        return balances.update_one({"user_id": user_id, "balance_id": balance_id}, {"$set": data})
    else:
        return balances.update_one({"user_id": user_id}, {"$set": data})

def balances_delete_one(user_id: int):
    return balances.delete_one({"user_id": user_id})


#Transaction.py
def transactions_find_one(user_id: int, balance_id: int, transaction_id: int):
    return transactions.find_one({"user_id": user_id, "balance_id": balance_id, "transaction_id": transaction_id, "is_deleted": False})

def transactions_find(user_id: int, balance_id: int):
    return transactions.find({"user_id": user_id, "balance_id": balance_id, "is_deleted": False})

def transactions_update_one(user_id: int, balance_id: int, transaction_id: int, data: dict):
    return transactions.update_one({"user_id": user_id, "balance_id": balance_id, "transaction_id": transaction_id}, {"$set": data})

def transactions_delete_one(user_id: int, balance_id: int, transaction_id: int):
    return transactions.delete_one({"user_id": user_id, "balance_id": balance_id, "transaction_id": transaction_id})


#Trains.py
def trains_find_one(train_id: int):
    return trains.find_one({"train_id": train_id, "is_deleted": False})

def trains_update_one(train_id: int, data: dict):
    return trains.update_one({"train_id": train_id}, {"$set": data})

def stations_update_many(train_id: int, data: dict):
    return stations.update_many({"train_id": train_id}, {"$set": data})

def travels_update_many(train_id: int, data: dict):
    return travels.update_many({"train_id": train_id}, {"$set": data})

def trains_delete_one(train_id: int):
    return trains.delete_one({"train_id": train_id})

def stations_delete_many(train_id: int):
    return stations.delete_many({"train_id": train_id})

def travels_delete_many(train_id: int):
    return travels.delete_many({"train_id": train_id})


#Stations.py
def stations_find_one(train_id: int, station_id: int):
    return stations.find_one({"train_id": train_id, "station_id": station_id, "is_deleted": False})

def stations_update_one(train_id: int, station_id: int, data: dict):
    return stations.update_one({"train_id": train_id, "station_id": station_id}, {"$set": data})

def stations_delete_one(train_id: int, station_id: int):
    return stations.delete_one({"train_id": train_id, "station_id": station_id})


#Travels.py
def travels_find(train_id: int):
    return travels.find({"train_id": train_id, "is_deleted": False})

def travels_find_one(train_id: int, travel_id: int):
    return travels.find_one({"train_id": train_id, "travel_id": travel_id, "is_deleted": False})

def travels_update_one(train_id: int, travel_id: int, data: dict):
    return travels.update_one({"train_id": train_id, "travel_id": travel_id}, {"$set": data})

def travels_delete_one(train_id: int, travel_id: int):
    return travels.delete_one({"train_id": train_id, "travel_id": travel_id})



#Payments.py
def payments_find(user_id: int):
    return payments.find({"user_id": user_id, "is_deleted": False})

def travels_find_by_id(travel_id: int):
    return travels.find_one({"travel_id": travel_id, "is_deleted": False})

def payments_find_one(user_id: int, payment_id: int):
    return payments.find_one({"user_id": user_id, "payment_id": payment_id, "is_deleted": False})

def payments_update_one(user_id: int, payment_id: int, data: dict):
    return payments.update_one({"user_id": user_id, "payment_id": payment_id}, {"$set": data})

def payments_delete_one(user_id: int, payment_id: int):
    return payments.delete_one({"user_id": user_id, "payment_id": payment_id})