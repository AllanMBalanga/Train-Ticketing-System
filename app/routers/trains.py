from fastapi import APIRouter, status, HTTPException, Depends
from ..body import Train, get_next_sequence, TokenData
from ..updates import TrainPut
from ..response import TrainResponse, TrainAdminResponse
from typing import List, Union
from datetime import datetime
from ..queries import trains, trains_find_one, trains_update_one, trains_delete_one, stations_delete_many, stations_update_many, travels_delete_many, travels_update_many
from ..status_codes import validate_train_exists, validate_required_roles
from ..oauth2 import get_current_user

router = APIRouter(
    prefix="/trains",
    tags=["Trains"]
)

trains.create_index("train_id", unique=True)

@router.get("/", response_model=List[Union[TrainResponse, TrainAdminResponse]])
def get_trains(current_user: TokenData = Depends(get_current_user)):
    validate_required_roles(current_user.role, ["user", "admin"])
    
    existing_trains = trains.find({"is_deleted": False})

    if current_user.role == "user":
        return [TrainResponse(**i) for i in existing_trains]
    else:
        return [TrainAdminResponse(**i) for i in existing_trains]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TrainAdminResponse)
def create_trains(train: Train, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        train_id = get_next_sequence("train_id")
        doc = {
            "train_id": train_id,
            **train.dict(),
            "created_at": datetime.utcnow(),
            "updated_at": None,
            "is_deleted": False
        }

        result = trains.insert_one(doc)
        created_transaction = trains.find_one({"_id": result.inserted_id})

        return created_transaction
    
    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/{train_id}", response_model=Union[TrainResponse, TrainAdminResponse])
def get_train(train_id: int, current_user: TokenData = Depends(get_current_user)):
    validate_required_roles(current_user.role, ["user", "admin"])

    train = trains_find_one(train_id)
    validate_train_exists(train, train_id)

    if current_user.role == "user":
        return TrainResponse(**train)
    else:
        return TrainAdminResponse(**train)

@router.put("/{train_id}", response_model=TrainAdminResponse)
def put_train(train_id: int, train: TrainPut, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        train_data = train.dict()
        train_data["updated_at"] = datetime.utcnow()

        trains_update_one(train_id, train_data)
        updated_train = trains_find_one(train_id)
        
        return updated_train
    
    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{train_id}", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_train(train_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        trains_delete_one(train_id)
        stations_delete_many(train_id)
        travels_delete_many(train_id)

        return 
    
    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{train_id}/delete", status_code=status.HTTP_200_OK)
def soft_delete_train(train_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        trains_update_one(train_id, {"is_deleted": True})
        stations_update_many(train_id, {"is_deleted": True})
        travels_update_many(train_id, {"is_deleted": True})

        return {"detail": f"Train with id {train_id} and related records softly deleted"}
    
    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
