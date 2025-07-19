from fastapi import APIRouter, status, HTTPException
from ..body import Train, get_next_sequence
from ..updates import TrainPut
from ..response import TrainResponse, TrainAdminResponse
from typing import List
from datetime import datetime
from ..queries import trains, trains_find_one, trains_update_one, trains_delete_one, stations_delete_many, stations_update_many, travels_delete_many, travels_update_many
from ..status_codes import validate_train_exists

router = APIRouter(
    prefix="/trains",
    tags=["Trains"]
)

trains.create_index("train_id", unique=True)

@router.get("/", response_model=List[TrainResponse])
def get_trains():
    existing_trains = trains.find()

    return existing_trains

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TrainAdminResponse)
def create_trains(train: Train):
    try:
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

@router.get("/{train_id}", response_model=TrainResponse)
def get_train(train_id: int):
    train = trains_find_one(train_id)
    validate_train_exists(train, train_id)

    return train

@router.put("/{train_id}", response_model=TrainAdminResponse)
def put_train(train_id: int, train: TrainPut):
    try:
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
def hard_delete_train(train_id: int):
    try:
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
def soft_delete_train(train_id: int):
    try:
        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        trains_update_one(train_id, {"is_deleted": True})
        stations_update_many(train_id, {"is_deleted": True})
        travels_update_many(train_id, {"is_deleted": True})

        return {"Detail": f"Train with id {train_id} and related records softly deleted"}
    
    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
