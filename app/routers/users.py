from pymongo import errors
from fastapi import HTTPException, status, APIRouter
from typing import List
from ..updates import UserPatch, UserPut
from ..database import db
from ..status_codes import validate_user_exists
from ..response import UserResponse
from ..body import User, get_next_sequence

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

users = db.users

users.create_index("email", unique=True)
users.create_index("user_id", unique=True)

@router.get("/", response_model=List[UserResponse])
def get_all():
    user = users.find()
    
    return user

@router.get("/{user_id}", response_model=UserResponse)
def get_one_user(user_id: int):
    user = users.find_one({"user_id": user_id})
    validate_user_exists(user, user_id)
    
    return user

@router.post("/", response_model=UserResponse)
def create_user(user: User):
    try:
        user_id = get_next_sequence("user_id")
        doc = user.dict()
        doc["user_id"] = user_id

        result = users.insert_one(doc)
        created_user = users.find_one({"_id": result.inserted_id})
        return created_user
    
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
    except errors.DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
        
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(user_id: int):
    try:
        user = users.find_one({"user_id": user_id})
        validate_user_exists(user, user_id)
        users.delete_one(user)
        return
    
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@router.put("/{user_id}", response_model=UserResponse)
def put_user(user_id: int, user: UserPut):
    try:
        existing_user = users.find_one()
        validate_user_exists(existing_user, user_id)

        users.update_one({"user_id": user_id}, {"$set": user.dict()})
        updated_user = users.find_one({"user_id": user_id})

        return updated_user

    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/{user_id}", response_model=UserResponse)
def put_user(user_id: int, user: UserPatch):
    try:
        existing_user = users.find_one()
        validate_user_exists(existing_user, user_id)

        users.update_one({"user_id": user_id}, {"$set": user.dict(exclude_unset=True)})
        updated_user = users.find_one({"user_id": user_id})

        return updated_user

    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


# users.create_index("email", unique=True)
# users.insert_one({"name":"Allan", "email": "jun@gmail.com"})

# for user in users.find():
#     print(user)