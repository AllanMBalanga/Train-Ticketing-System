from datetime import datetime
from pymongo import errors
from fastapi import HTTPException, status, APIRouter
from typing import List
from ..updates import UserPatch, UserPut
from ..status_codes import validate_user_exists
from ..response import UserBalanceResponse, UserResponse
from ..body import User, get_next_sequence, UserCreate
from ..utils import hash
from ..queries import users_find_one, users, balances, transactions

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


users.create_index("email", unique=True)
users.create_index("user_id", unique=True)

@router.get("/", response_model=List[UserResponse])
def get_all():
    user = users.find()
    
    return user

@router.post("/", response_model=UserBalanceResponse)
def create_user(user: User):
    try:
        existing_user = users.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Email already in use"
            )
        
        user.password = hash(user.password)
        user_id = get_next_sequence("user_id")
        doc = {
            "user_id": user_id,
            **user.dict(),
            "created_at": datetime.utcnow(),
            "updated_at": None,
            "is_deleted": False
        }

        result = users.insert_one(doc)
        created_user = users.find_one({"_id": result.inserted_id})

        #Creates balances upon creation of account
        balance_id = get_next_sequence("balance_id")
        balance_doc = {
            "user_id": user_id, 
            "balance_id": balance_id, 
            "total": 0, 
            "created_at": datetime.utcnow(),
            "updated_at": None, 
            "is_deleted": False
        }

        balance_result = balances.insert_one(balance_doc)
        created_balance = balances.find_one({"_id": balance_result.inserted_id})

        return {
            "user":created_user, 
            "balance":created_balance
        }
    
    except HTTPException:
        raise 
    
    except errors.DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.get("/{user_id}", response_model=UserResponse)
def get_one_user(user_id: int):
    user = users_find_one(user_id)
    validate_user_exists(user, user_id)
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
def put_user(user_id: int, user: UserPut):
    try:
        user.password = hash(user.password)
        existing_user = users_find_one(user_id)
        validate_user_exists(existing_user, user_id)

        put_data = user.dict()
        put_data["updated_at"] = datetime.utcnow()

        users.update_one({"user_id": user_id}, {"$set": put_data})
        updated_user = users_find_one(user_id)

        return updated_user

    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/{user_id}", response_model=UserResponse)
def put_user(user_id: int, user: UserPatch):
    try:
        if user.password:
            user.password = hash(user.password)
            
        existing_user = users_find_one(user_id)
        validate_user_exists(existing_user, user_id)

        patch_data = user.dict(exclude_unset=True)
        patch_data["updated_at"] = datetime.utcnow()

        users.update_one({"user_id": user_id}, {"$set": patch_data})
        updated_user = users_find_one(user_id)

        return updated_user

    except HTTPException:
        raise 
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_user(user_id: int):
    try:
        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        users.delete_one({"user_id": user_id})
        balances.delete_one({"user_id": user_id})
        transactions.delete_many({"user_id": user_id})

        return
    
    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@router.delete("/{user_id}/delete", status_code=status.HTTP_200_OK)
def soft_delete_user(user_id: int):
    try:
        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        #Update users, balances, transactions is_deleted
        users.update_one({"user_id": user_id}, {"$set": {"is_deleted": True}})
        balances.update_one({"user_id": user_id}, {"$set": {"is_deleted": True}})
        transactions.update_many({"user_id": user_id}, {"$set": {"is_deleted": True}})
        
        return {"Detail": f"User with id {user_id} and related records softly deleted"}
    
    except HTTPException:
        raise 
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# users.create_index("email", unique=True)
# users.insert_one({"name":"Allan", "email": "jun@gmail.com"})

# for user in users.find():
#     print(user)