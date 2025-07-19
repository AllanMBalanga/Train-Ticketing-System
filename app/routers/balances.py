from fastapi import APIRouter, HTTPException, status, Depends
from ..response import BalanceResponse, BalanceAdminResponse
from ..updates import BalancePut
from ..status_codes import validate_user_exists, validate_logged_in_user, validate_required_roles
from datetime import datetime
from ..queries import balances, balances_find_one, users_find_one, balances_delete_one, balances_update_one
from typing import Union
from ..oauth2 import get_current_user
from ..body import TokenData

router = APIRouter(
    prefix="/users/{user_id}/balances",
    tags=["Balances"]
)

balances.create_index("balance_id", unique=True)

@router.get("/", response_model=Union[BalanceResponse, BalanceAdminResponse])
def get_balance(user_id: int, current_user: TokenData = Depends(get_current_user)):
    validate_required_roles(current_user.role, ["user", "admin"])
    if current_user.role == "user":
        validate_logged_in_user(current_user.id, user_id)

    user = users_find_one(user_id)
    validate_user_exists(user, user_id)

    balance = balances_find_one(user_id)

    if current_user.role == "user":
        return BalanceResponse(**balance)
    else:
        return BalanceAdminResponse(**balance)


@router.put("/", response_model=BalanceAdminResponse)
def put_balance(user_id: int, balance: BalancePut, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])
 
        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        put_data = balance.dict()
        put_data["updated_at"] = datetime.utcnow()

        balances_update_one(user_id, put_data)
        balance = balances_find_one(user_id)

        return balance
    
    except HTTPException:
        raise 
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_balance(user_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        balances_delete_one(user_id)

        return

    except HTTPException:
        raise 
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/delete", status_code=status.HTTP_200_OK)
def soft_delete_balance(user_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["user", "admin"])
        if current_user.role == "user":
            validate_logged_in_user(current_user.id, user_id)

        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        balances_update_one(user_id, {"is_deleted": True})
        
        return {"detail": "User's balance softly deleted"}
    
    except HTTPException:
        raise 
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

