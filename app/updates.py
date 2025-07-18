from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class UserPut(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class BalancePut(BaseModel):
    total: float

class TransactionPut(BaseModel):
    type: Literal["withdraw", "deposit"] = "deposit"
    amount: float

class TrainPut(BaseModel):
    name: str

class StationPut(BaseModel):
    name: str
    position: int

class TravelPut(BaseModel):
    departure_id: int
    arrival_id: int

class PaymentPut(BaseModel):
    travel_id: int


class UserPatch(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# class BalancePatch(BaseModel):
#     total: Optional[float] = None

class TransactionPatch(BaseModel):
    type: Optional[Literal["withdraw", "deposit"]] = None
    amount: Optional[float] = None

# class TrainPatch(BaseModel):
#     name: Optional[str] = None

class StationPatch(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = None

class TravelPatch(BaseModel):
    departure_id: Optional[int] = None
    arrival_id: Optional[int] = None

# class PaymentPatch(BaseModel):
#     travel_id: Optional[int] = None


