from pydantic import BaseModel, EmailStr
from typing import Literal
from .database import db
from pymongo import ReturnDocument
from datetime import datetime

#FOR CREATING AUTO INCREMENTED IDs
def get_next_sequence(name: str):
    counter = db.counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        return_document=ReturnDocument.AFTER,
        upsert=True  # creates it if missing
    )
    return counter["seq"]


#users/
class User(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserCreate(User):
    user_id: int
    created_at: datetime
    is_deleted: bool = False


#users/{user_id}/balances - Get only
class Balance(BaseModel):
    total: float    
    user_id: int
    balance_id: int
    created_at: datetime
    is_deleted: bool = False

#users/{user_id}/balances/{balance_id}/actions
class Transaction(BaseModel):
    type: Literal["withdraw", "deposit"] = "deposit"
    amount: float

#transits
class Transit(BaseModel):
    name: str

#transits/{transit_id}/stations
class Station(BaseModel):
    name: str
    position: int

#travels
class Travel(BaseModel):
    departure_id: str
    arrival_id: str
    total: float

#users/{user_id}/payments
class Payment(BaseModel):
    travel_id: str