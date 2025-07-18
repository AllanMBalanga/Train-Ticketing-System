from fastapi import status, HTTPException

def validate_user_exists(user, user_id: int = None):
    if not user:
        if user_id:
            detail = f"User with id {user_id} was not found"
        else:
            detail = "User was not found"
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

def validate_balance_exists(balance, balance_id: int = None):
    if not balance:
        if balance_id:
            detail = f"Balance with id {balance_id} was not found"
        else:
            detail = "Balance was not found"
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
def validate_transaction_exists(transaction, transaction_id: int = None):
    if not transaction:
        if transaction_id:
            detail = f"Transaction with id {transaction_id} was not found"
        else:
            detail = "Transaction was not found"
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
def validate_train_exists(train, train_id: int = None):
    if not train:
        if train_id:
            detail = f"Train with id {train_id} was not found"
        else:
            detail = "Train was not found"
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
def validate_station_exists(station, station_id: int = None):
    if not station:
        if station_id:
            detail = f"Station with id {station_id} was not found"
        else:
            detail = "Station was not found"
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
def validate_travel_exists(travel, travel_id: int = None):
    if not travel:
        if travel_id:
            detail = f"Travel with id {travel_id} was not found"
        else:
            detail = "Travel was not found"
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

def validate_payment_exists(payment, payment_id: int = None):
    if not payment:
        if payment_id:
            detail = f"Payment with id {payment_id} was not found"
        else:
            detail = "Payment was not found"
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )