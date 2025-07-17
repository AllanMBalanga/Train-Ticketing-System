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