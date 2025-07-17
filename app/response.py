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


class UserResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    user_id: int
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class BalanceResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    user_id: int
    balance_id: int
    total: float
    created_at: datetime
    updated_at: Optional[datetime] = None

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
    created_at: datetime
    updated_at: Optional[datetime] = None

#TRANSACTIONS POST
class TransactionBalanceResponse(BaseModel):
    transaction: TransactionResponse
    balance: BalanceResponse


class TransitResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    name: str


class StationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    transit_id: int
    name: str
    position: int


class TravelResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    departure_id: int
    arrival_id: int
    total: float


class PaymentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: PydanticObjectId = Field(alias="_id")
    user_id: int
    travel_id: int

