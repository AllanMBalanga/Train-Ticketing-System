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
