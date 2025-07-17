from ..database import balances, users
from fastapi import APIRouter, HTTPException, status
from ..response import BalanceResponse
from ..updates import BalancePut
from ..status_codes import validate_user_exists
from datetime import datetime

router = APIRouter(
    prefix="/users/{user_id}/balances",
    tags=["Balances"]
)

@router.get("/", response_model=BalanceResponse)
def get_balance(user_id: int):
    user = users.find_one({"user_id": user_id})
    validate_user_exists(user, user_id)

    balance = balances.find_one({"user_id": user_id})

    return balance

@router.put("/", response_model=BalanceResponse)
def put_balance(user_id: int, balance: BalancePut):
    try:
        user = users.find_one({"user_id": user_id})
        validate_user_exists(user, user_id)

        put_data = balance.dict()
        put_data["updated_at"] = datetime.utcnow()

        balances.update_one({"user_id": user_id}, {"$set": put_data})
        balance = balances.find_one({"user_id": user_id})

        return balance
    
    except HTTPException:
        raise 
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_balance(user_id: int):
    try:
        user = users.find_one({"user_id": user_id})
        validate_user_exists(user, user_id)

        balances.delete_one({"user_id": user_id})

        return

    except HTTPException:
        raise 
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/delete", status_code=status.HTTP_200_OK)
def soft_delete_balance(user_id: int):
    try:
        user = users.find_one({"user_id": user_id})
        validate_user_exists(user, user_id)

        balances.update_one({"user_id": user_id}, {"$set": {"is_deleted": True}})
        
        return {"Detail": "User's balance softly deleted"}
    
    except HTTPException:
        raise 
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

