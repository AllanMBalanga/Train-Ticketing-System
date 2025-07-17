from ..response import TransactionResponse, TransactionBalanceResponse
from ..body import Transaction, get_next_sequence
from fastapi import APIRouter, status, HTTPException
from ..status_codes import validate_balance_exists, validate_user_exists, validate_transaction_exists
from ..database import transactions, users, balances
from datetime import datetime
from typing import List


router = APIRouter(
    prefix="/users/{user_id}/balances/{balance_id}/transactions",
    tags=["Transactions"]
)

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(user_id: int, balance_id: int):
    user = users.find_one({"user_id": user_id})
    validate_user_exists(user, user_id)

    balance = balances.find_one({"user_id": user_id,"balance_id": balance_id})
    validate_balance_exists(balance, balance_id)

    existing_transactions = transactions.find({"user_id": user_id, "balance_id": balance_id})
    
    return existing_transactions

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TransactionBalanceResponse)
def create_transaction(user_id: int, balance_id: int, action: Transaction):
    try:
        transaction_id = get_next_sequence("transaction_id")

        user = users.find_one({"user_id": user_id})
        validate_user_exists(user, user_id)

        balance = balances.find_one({"user_id": user_id, "balance_id": balance_id})
        validate_balance_exists(balance, balance_id)

        doc = {
            **action.dict(),
            "user_id": user_id, 
            "balance_id": balance_id, 
            "transaction_id": transaction_id, 
            "created_at": datetime.utcnow(),
            "is_deleted": False
        }
        
        result = transactions.insert_one(doc)
        created_transaction = transactions.find_one({"_id": result.inserted_id})
          
        total_balance = balance["total"]

        if action.type == "deposit":
            new_balance =  total_balance + action.amount
        else:
            if total_balance - action.amount < 0:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Total balance not sufficient")
            else:
                new_balance = total_balance - action.amount
        
        balances.update_one({"user_id": user_id, "balance_id": balance_id}, {"$set": {"total": new_balance}})
        updated_balance = balances.find_one({"user_id": user_id, "balance_id": balance_id})
        
        return {
            "transaction": created_transaction,
            "balance": updated_balance
        }

    except HTTPException:
        raise HTTPException

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transactions(user_id: int, balance_id: int, transaction_id: int):
    user = users.find_one({"user_id": user_id})
    validate_user_exists(user, user_id)

    balance = balances.find_one({"user_id": user_id,"balance_id": balance_id})
    validate_balance_exists(balance, balance_id)

    existing_transaction = transactions.find({"user_id": user_id, "balance_id": balance_id, "transaction_id": transaction_id})
    validate_transaction_exists(existing_transaction, transaction_id)

    return existing_transaction

@router.delete("/{transaction_id}/delete", status_code=status.HTTP_200_OK)
def soft_delete_transaction(user_id: int, balance_id: int, transaction_id: int):
    try:
        user = users.find_one({"user_id": user_id})
        validate_user_exists(user, user_id)

        balance = balances.find_one({"user_id": user_id,"balance_id": balance_id})
        validate_balance_exists(balance, balance_id)
        
        existing_transaction = transactions.find({"user_id": user_id, "balance_id": balance_id, "transaction_id": transaction_id})
        validate_transaction_exists(existing_transaction, transaction_id)

        transactions.update_one({"user_id": user_id, "balance_id": balance_id, "transaction_id": transaction_id}, {"$set": {"is_deleted": True}})

        return {"Detail": "User's transaction softly deleted"}

    except HTTPException:
        raise HTTPException

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
