from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class UserPut(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

# class BalancePut(BaseModel):
#     total: float

class ActionPut(BaseModel):
    type: Literal["withdraw", "deposit"] = "deposit"
    amount: float

class TransitPut(BaseModel):
    name: str

class StationPut(BaseModel):
    name: str
    position: int

class StationPatch(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = None


class TravelPut(BaseModel):
    departure_id: int
    arrival_id: int
    total: float

class PaymentPut(BaseModel):
    travel_id: int


class UserPatch(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# class BalancePatch(BaseModel):
#     total: Optional[float] = None

class ActionPatch(BaseModel):
    type: Optional[Literal["withdraw", "deposit"]] = None
    amount: Optional[float] = None

class TransitPatch(BaseModel):
    name: Optional[str] = None

class TravelPut(BaseModel):
    departure_id: Optional[int] = None
    arrival_id: Optional[int] = None
    total: Optional[float] = None

class PaymentPatch(BaseModel):
    travel_id: Optional[int] = None