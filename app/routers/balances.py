from ..database import balances, users
from fastapi import APIRouter, HTTPException, status
from ..response import BalanceResponse
from typing import List
from ..status_codes import validate_user_exists

router = APIRouter(
    prefix="/users/{user_id}/balances",
    tags=["Balances"]
)

@router.get("/", response_model=List[BalanceResponse])
def get_balances(user_id: int):
    user = users.find_one({"user_id": user_id})
    validate_user_exists(user, user_id)

    balance = balances.find_one({"user_id": user_id})

    return balance

@router.delete("/delete", status_code=status.HTTP_200_OK)
def soft_delete_balance(user_id: int):
    try:
        user = users.find_one({"user_id": user_id})
        validate_user_exists(user, user_id)

        balances.update_one({"user_id": user_id}, {"$set": {"is_deleted": True}})
        
        return {"Detail": "User's balance softly deleted"}
    
    except HTTPException:
        raise HTTPException
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

