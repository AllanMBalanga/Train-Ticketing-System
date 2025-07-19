from bson import ObjectId
from typing import Annotated, Any, Callable, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from pydantic_core import core_schema
from datetime import datetime

class _ObjectIdPydanticAnnotation:
    # Based on https://docs.pydantic.dev/latest/usage/types/custom/#handling-third-party-types.

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(input_value: str) -> ObjectId:
            return ObjectId(input_value)

        return core_schema.union_schema(
            [
                # check if it's an instance first before doing any further work
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )

PydanticObjectId = Annotated[
    ObjectId, _ObjectIdPydanticAnnotation
]

#USER RESPONSES
class UserResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    user_id: int
    email: EmailStr
    first_name: str
    last_name: str

class BalanceResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    user_id: int
    balance_id: int
    total: float

#USERS POST
class UserBalanceResponse(BaseModel):
    user: UserResponse
    balance: BalanceResponse


class TransactionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    user_id: int
    balance_id: int
    transaction_id: int
    type: Literal["withdraw", "deposit"]
    amount: float

#TRANSACTIONS POST
class TransactionBalanceResponse(BaseModel):
    transaction: TransactionResponse
    balance: BalanceResponse

class TrainResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    train_id: int
    name: str

class StationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    train_id: int
    station_id: int
    name: str
    position: int

class TravelResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    train_id: int
    travel_id: int
    departure_id: int
    arrival_id: int
    total: float

class PaymentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    payment_id: int
    user_id: int
    travel_id: int

class PaymentBalanceReponse(BaseModel):
    payment: PaymentResponse
    balance: BalanceResponse


#ADMIN RESPONSES
class UserAdminResponse(UserResponse):
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool

class BalanceAdminResponse(BalanceResponse):
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool

class TransactionAdminResponse(TransactionResponse):
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool

class TransactionBalanceAdminResponse(BaseModel):
    transaction: TransactionAdminResponse
    balance: BalanceAdminResponse

class TrainAdminResponse(TrainResponse):
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool

class StationAdminResponse(StationResponse):
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool

class TravelAdminResponse(TravelResponse):
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool

class PaymentAdminResponse(PaymentResponse):
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool
