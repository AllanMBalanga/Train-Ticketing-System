from datetime import datetime
from pymongo import errors
from fastapi import HTTPException, status, APIRouter, Depends
from typing import List, Union
from ..updates import UserPatch, UserPut
from ..status_codes import validate_user_exists, validate_logged_in_user, validate_required_roles
from ..response import UserAdminResponse, UserBalanceResponse, UserResponse
from ..body import User, get_next_sequence, TokenData
from ..utils import hash
from ..queries import users, balances, balances_delete_one, balances_update_one, transactions_update_many, transactions_delete_many, users_find_one, users_delete_one, users_update_one, payments_delete_many, payments_update_many
from ..oauth2 import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

users.create_index("email", unique=True)
users.create_index("user_id", unique=True)

@router.get("/", response_model=List[Union[UserResponse, UserAdminResponse]])
def get_all(current_user: TokenData = Depends(get_current_user)):
    validate_required_roles(current_user.role, ["user", "admin"])
    
    user = users.find({"is_deleted": False})
    
    if current_user.role == "user":
        return [UserResponse(**i) for i in user]
    else:
        return [UserAdminResponse(**i) for i in user]

@router.post("/", response_model=UserBalanceResponse, status_code=status.HTTP_201_CREATED)
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
            "role": "user",
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


@router.get("/{user_id}", response_model=Union[UserResponse, UserAdminResponse])
def get_one_user(user_id: int, current_user: TokenData = Depends(get_current_user)):
    validate_required_roles(current_user.role, ["user", "admin"])
    if current_user.role == "user":
        validate_logged_in_user(current_user.id, user_id)

    user = users_find_one(user_id)
    validate_user_exists(user, user_id)
    
    if current_user.role == "user":
        return UserResponse(**user)
    else:
        return UserAdminResponse(**user)

@router.put("/{user_id}", response_model=Union[UserResponse, UserAdminResponse])
def put_user(user_id: int, user: UserPut, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["user", "admin"])
        if current_user.role == "user":
            validate_logged_in_user(current_user.id, user_id)
        
        user.password = hash(user.password)
        existing_user = users_find_one(user_id)
        validate_user_exists(existing_user, user_id)

        put_data = user.dict()
        put_data["updated_at"] = datetime.utcnow()

        users_update_one(user_id, put_data)
        updated_user = users_find_one(user_id)

        if current_user.role == "user":
            return UserResponse(**updated_user)
        else:
            return UserAdminResponse(**updated_user)

    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/{user_id}", response_model=Union[UserResponse, UserAdminResponse])
def patch_user(user_id: int, user: UserPatch, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["user", "admin"])
        if current_user.role == "user":
            validate_logged_in_user(current_user.id, user_id)

        if user.password:
            user.password = hash(user.password)
            
        existing_user = users_find_one(user_id)
        validate_user_exists(existing_user, user_id)

        patch_data = user.dict(exclude_unset=True)
        patch_data["updated_at"] = datetime.utcnow()

        users_update_one(user_id, patch_data)
        updated_user = users_find_one(user_id)

        if current_user.role == "user":
            return UserResponse(**updated_user)
        else:
            return UserAdminResponse(**updated_user)


    except HTTPException:
        raise 
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_user(user_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        users_delete_one(user_id)
        balances_delete_one(user_id)
        transactions_delete_many(user_id)
        payments_delete_many(user_id)

        return
    
    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@router.delete("/{user_id}/delete", status_code=status.HTTP_200_OK)
def soft_delete_user(user_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["user", "admin"])
        if current_user.role == "user":
            validate_logged_in_user(current_user.id, user_id)

        user = users_find_one(user_id)

        validate_user_exists(user, user_id)

        #Update users, balances, transactions is_deleted
        users_update_one(user_id, {"is_deleted": True})
        balances_update_one(user_id, {"is_deleted": True})
        transactions_update_many(user_id, {"is_deleted": True})
        payments_update_many(user_id, {"is_deleted": True})

        return {"detail": f"User with id {user_id} and related records softly deleted"}
    
    except HTTPException:
        raise 
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
