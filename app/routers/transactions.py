from ..response import TransactionResponse, TransactionBalanceResponse, TransactionBalanceAdminResponse, TransactionAdminResponse
from ..body import Transaction, get_next_sequence, TokenData
from fastapi import APIRouter, status, HTTPException, Depends
from ..status_codes import validate_logged_in_user, validate_required_roles, validate_balance_exists, validate_user_exists, validate_transaction_exists
from ..queries import transactions, balances_update_one, transactions_delete_one, transactions_update_one, transactions_find, users_find_one, balances_find_one, transactions_find_one
from datetime import datetime
from typing import List, Union
from ..updates import TransactionPatch, TransactionPut
from ..oauth2 import get_current_user

router = APIRouter(
    prefix="/users/{user_id}/balances/{balance_id}/transactions",
    tags=["Transactions"]
)

transactions.create_index("transaction_id", unique=True)

@router.get("/", response_model=List[Union[TransactionResponse, TransactionAdminResponse]])
def get_transactions(user_id: int, balance_id: int, current_user: TokenData = Depends(get_current_user)):
    validate_required_roles(current_user.role, ["user", "admin"])
    if current_user.role == "user":
        validate_logged_in_user(current_user.id, user_id)

    user = users_find_one(user_id)
    validate_user_exists(user, user_id)

    balance = balances_find_one(user_id, balance_id)
    validate_balance_exists(balance, balance_id)

    existing_transactions = transactions_find(user_id, balance_id)
    
    if current_user.role == "user":
        return [TransactionResponse(**t) for t in existing_transactions]
    else:
        return [TransactionAdminResponse(**t) for t in existing_transactions]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TransactionBalanceResponse)
def create_transaction(user_id: int, balance_id: int, transaction: Transaction, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["user"])
        validate_logged_in_user(current_user.id, user_id)

        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        balance = balances_find_one(user_id, balance_id)
        validate_balance_exists(balance, balance_id)

        transaction_id = get_next_sequence("transaction_id")
        doc = {
            "user_id": user_id, 
            "balance_id": balance_id, 
            "transaction_id": transaction_id, 
            **transaction.dict(),
            "created_at": datetime.utcnow(),
            "updated_at": None,
            "is_deleted": False
        }
        
        result = transactions.insert_one(doc)
        created_transaction = transactions.find_one({"_id": result.inserted_id})
          
        total_balance = balance["total"]

        if transaction.type == "deposit":
            new_balance =  total_balance + transaction.amount
        else:
            if total_balance - transaction.amount < 0:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Total balance not sufficient")
            else:
                new_balance = total_balance - transaction.amount
                
        balances_update_one(user_id=user_id, balance_id=balance_id, data={"total": new_balance})
        updated_balance = balances_find_one(user_id, balance_id)
        
        return {
            "transaction": created_transaction,
            "balance": updated_balance
        }

    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.get("/{transaction_id}", response_model=Union[TransactionResponse, TransactionAdminResponse])
def get_transactions(user_id: int, balance_id: int, transaction_id: int, current_user: TokenData = Depends(get_current_user)):
    validate_required_roles(current_user.role, ["user", "admin"])
    if current_user.role == "user":
        validate_logged_in_user(current_user.id, user_id)

    user = users_find_one(user_id)
    validate_user_exists(user, user_id)

    balance = balances_find_one(user_id, balance_id)
    validate_balance_exists(balance, balance_id)

    existing_transaction = transactions_find_one(user_id, balance_id, transaction_id)
    validate_transaction_exists(existing_transaction, transaction_id)

    if current_user.role == "user":
        return TransactionResponse(**existing_transaction)
    else:
        return TransactionAdminResponse(**existing_transaction)


@router.put("/{transaction_id}", response_model=TransactionBalanceAdminResponse)
def put_transaction(user_id: int, balance_id: int, transaction_id: int, transaction: TransactionPut, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        balance = balances_find_one(user_id, balance_id)
        validate_balance_exists(balance, balance_id)

        existing_transaction = transactions_find_one(user_id, balance_id, transaction_id)
        validate_transaction_exists(existing_transaction, transaction_id)

        #reset balance before the transaction
        if existing_transaction["type"] == "withdraw":
            balance["total"] += existing_transaction["amount"]
        else:
            balance["total"] -= existing_transaction["amount"]
        
        if transaction.type == "withdraw":
            if balance["total"] - transaction.amount < 0:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Insufficient balance")
            balance["total"] -= transaction.amount
        else:
            balance["total"] += transaction.amount

        put_data = transaction.dict()
        put_data["updated_at"] = datetime.utcnow()

        transactions_update_one(user_id, balance_id, transaction_id, put_data)
        updated_transaction = transactions_find_one(user_id, balance_id, transaction_id)

        balances_update_one(user_id=user_id, balance_id=balance_id, data={"total": balance["total"], "updated_at": datetime.utcnow()})
        updated_balance = balances_find_one(user_id, balance_id)

        return {
            "transaction": updated_transaction,
            "balance": updated_balance
        }
    
    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/{transaction_id}", response_model=TransactionBalanceAdminResponse)
def put_transaction(user_id: int, balance_id: int, transaction_id: int, transaction: TransactionPatch, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        balance = balances_find_one(user_id, balance_id)
        validate_balance_exists(balance, balance_id)

        existing_transaction = transactions_find_one(user_id, balance_id, transaction_id)
        validate_transaction_exists(existing_transaction, transaction_id)

        patch_data = transaction.dict(exclude_unset=True)
        patch_data["updated_at"] = datetime.utcnow()

        #reset balance before the transaction
        if "type" in patch_data:
            if existing_transaction["type"] == "withdraw":
                balance["total"] += existing_transaction["amount"]
            else:
                balance["total"] -= existing_transaction["amount"]

        new_type = patch_data.get("type", existing_transaction["type"])
        new_amount = patch_data.get("amount", existing_transaction["amount"])

        if new_type == "withdraw":
            if balance["total"] - new_amount < 0:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Insufficient balance")
            balance["total"] -= new_amount
        else:
            balance["total"] += new_amount

        transactions_update_one(user_id, balance_id, transaction_id, patch_data)
        updated_transaction = transactions_find_one(user_id, balance_id, transaction_id)

        balances_update_one(user_id=user_id, balance_id=balance_id, data={"total": balance["total"], "updated_at": datetime.utcnow()})
        updated_balance = balances_find_one(user_id, balance_id)

        return {
            "transaction": updated_transaction,
            "balance": updated_balance
        }
    
    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_transaction(user_id: int, balance_id: int, transaction_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        balance = balances_find_one(user_id, balance_id)
        validate_balance_exists(balance, balance_id)

        existing_transaction = transactions_find_one(user_id, balance_id, transaction_id)
        validate_transaction_exists(existing_transaction, transaction_id)

        transactions_delete_one(user_id, balance_id, transaction_id)

        return 

    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{transaction_id}/delete", status_code=status.HTTP_200_OK)
def soft_delete_transaction(user_id: int, balance_id: int, transaction_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["user", "admin"])
        if current_user.role == "user":
            validate_logged_in_user(current_user.id, user_id)

        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        balance = balances_find_one(user_id, balance_id)
        validate_balance_exists(balance, balance_id)

        existing_transaction = transactions_find_one(user_id, balance_id, transaction_id)
        validate_transaction_exists(existing_transaction, transaction_id)

        transactions_update_one(user_id, balance_id, transaction_id, {"is_deleted": True})

        return {"detail": "User's transaction softly deleted"}

    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
