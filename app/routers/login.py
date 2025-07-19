from fastapi import APIRouter, status, HTTPException, Depends
from ..queries import users
from ..body import LoggedInToken
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..utils import verify
from ..oauth2 import create_token

router = APIRouter(
    prefix="/login",
    tags=["Login"]
)

@router.post("/", response_model=LoggedInToken)
def user_login(credentials: OAuth2PasswordRequestForm = Depends()):
    user = users.find_one({"email": credentials.username})

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    
    if not verify(credentials.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    
    access_token = create_token(data={"user_id": user["user_id"], "role": user["role"]})

    return {"access_token": access_token, "token_type": "bearer", "user_id": user["user_id"], "role": user["role"]}