from .database import users, balances, transactions, trains, stations, travels, payments

def users_find_one(user_id: int):
    return users.find_one({"user_id": user_id, "is_deleted": False})

def balances_find_one(user_id: int):
    return balances.find_one({"user_id": user_id, "is_deleted": False})

def transactions_find_one(transaction_id: int):
    return transactions.find_one({"transaction_id": transaction_id, "is_deleted": False})

def trains_find_one(train_id: int):
    return trains.find_one({"train_id": train_id, "is_deleted": False})

def stations_find_one(train_id: int, station_id: int):
    return stations.find_one({"train_id": train_id, "station_id": station_id, "is_deleted": False})

def travels_find_one(train_id: int, travel_id: int):
    return travels.find_one({"train_id": train_id, "travel_id": travel_id, "is_deleted": False})

def travels_find_by_id(travel_id: int):
    return travels.find_one({"travel_id": travel_id, "is_deleted": False})

def payments_find_one(user_id: int, payment_id: int):
    return payments.find_one({"user_id": user_id, "payment_id": payment_id, "is_deleted": False})