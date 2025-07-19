from fastapi import APIRouter, status, HTTPException, Depends
from ..queries import payments_delete_one, payments_update_one, payments_find, payments_find_one, payments, travels_find_by_id, users_find_one, balances, balances_find_one, balances_update_one
from ..body import get_next_sequence, Payment, TokenData
from ..updates import PaymentPut
from ..response import PaymentResponse, PaymentAdminResponse, PaymentBalanceResponse, PaymentBalanceAdminResponse 
from ..status_codes import validate_logged_in_user, validate_required_roles, validate_payment_exists, validate_user_exists, validate_balance_exists, validate_travel_exists
from typing import List, Union
from datetime import datetime
from ..oauth2 import get_current_user

router = APIRouter(
    prefix="/users/{user_id}/payments",
    tags=["Payments"]
)

payments.create_index("payment_id", unique=True)

@router.get("/", response_model=List[Union[PaymentResponse, PaymentAdminResponse]])
def get_payments(user_id: int, current_user: TokenData = Depends(get_current_user)):
    validate_required_roles(current_user.role, ["user", "admin"])
    if current_user.role == "user":
        validate_logged_in_user(current_user.id, user_id)

    existing_payments = payments_find(user_id)
    
    if current_user.role == "user":
        return [PaymentResponse(**i) for i in existing_payments]
    else:
        return [PaymentAdminResponse(**i) for i in existing_payments]

@router.post("/", response_model=PaymentBalanceResponse, status_code=status.HTTP_201_CREATED)
def create_payment(user_id: int, payment: Payment, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["user"])
        validate_logged_in_user(current_user.id, user_id)

        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        balance = balances_find_one(user_id)
        validate_balance_exists(balance, user_id)

        travel = travels_find_by_id(payment.travel_id)
        validate_travel_exists(travel, payment.travel_id)

        user_balance_total = balance["total"]
        travel_total = travel["total"]

        if user_balance_total - travel_total < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Total balance not sufficient")
        else:
            new_balance = user_balance_total - travel_total

        balances_update_one(user_id, {"total": new_balance})

        updated_balance = balances_find_one(user_id)

        payment_id = get_next_sequence("payment_id")
        payment_data = {
            "user_id": user_id,
            "payment_id": payment_id,
            **payment.dict(),
            "amount": travel_total,
            "created_at": datetime.utcnow(),
            "updated_at": None,
            "is_deleted": False
        }

        result = payments.insert_one(payment_data)
        created_payment = payments.find_one({"_id": result.inserted_id})

        return {
            "payment": created_payment,
            "balance": updated_balance
        }
    
    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@router.get("/{payment_id}", response_model=Union[PaymentResponse, PaymentAdminResponse])
def get_payment(user_id: int, payment_id: int, current_user: TokenData = Depends(get_current_user)):
    validate_required_roles(current_user.role, ["user", "admin"])
    if current_user.role == "user":
        validate_logged_in_user(current_user.id, user_id)

    user = users_find_one(user_id)
    validate_user_exists(user, user_id)

    payment = payments_find_one(user_id, payment_id)
    validate_payment_exists(payment, payment_id)

    if current_user.role == "user":
        return PaymentResponse(**payment)
    else:
        return PaymentAdminResponse(**payment)

@router.put("/{payment_id}", response_model=PaymentBalanceAdminResponse)
def put_payment(user_id: int, payment_id: int, payment: PaymentPut, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        existing_payment = payments_find_one(user_id, payment_id)
        validate_payment_exists(existing_payment, payment_id)

        existing_balance = balances_find_one(user_id)
        validate_balance_exists(existing_balance, user_id)

        # Revert previous travel total to balance (refund)
        previous_travel = travels_find_by_id(existing_payment["travel_id"])

        validate_travel_exists(previous_travel, existing_payment["travel_id"])

        reverted_balance_total = existing_balance["total"] + previous_travel["total"]

        # Fetch and validate new travel
        new_travel = travels_find_by_id(payment.travel_id)
        validate_travel_exists(new_travel, payment.travel_id)

        new_travel_total = new_travel["total"]

        if reverted_balance_total < new_travel_total:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Total balance not sufficient for updated travel")

        updated_balance_total = reverted_balance_total - new_travel_total
        
        balances_update_one(user_id, {"total": updated_balance_total})
        updated_balance = balances_find_one(user_id)

        updated_data = {
            "travel_id": payment.travel_id,
            "updated_at": datetime.utcnow()
        }

        payments_update_one(user_id, payment_id, updated_data)
        updated_payment = payments_find_one(user_id, payment_id)

        return {
            "payment": updated_payment,
            "balance": updated_balance
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_payment(user_id: int, payment_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])
        
        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        existing_payment = payments_find_one(user_id, payment_id)
        validate_payment_exists(existing_payment, payment_id)

        payments_delete_one(user_id, payment_id)

        return

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@router.delete("/{payment_id}/delete", status_code=status.HTTP_200_OK)
def soft_delete_payment(user_id: int, payment_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["user", "admin"])
        if current_user.role == "user":
            validate_logged_in_user(current_user.id, user_id)

        user = users_find_one(user_id)
        validate_user_exists(user, user_id)

        existing_payment = payments_find_one(user_id, payment_id)
        validate_payment_exists(existing_payment, payment_id)

        payments_update_one(user_id, payment_id, {"is_deleted": True})

        return {"detail": f"Payment with id {payment_id} softly deleted"}

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    