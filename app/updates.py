from pydantic import BaseModel, EmailStr
from typing import Optional

class UserPut(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserPatch(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
