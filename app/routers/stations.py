from fastapi import status, APIRouter, HTTPException
from ..body import Station, get_next_sequence
from ..updates import StationPatch, StationPut
from ..response import StationAdminResponse, StationUserResponse
from ..queries import stations_find_one, stations, trains_find_one
from ..status_codes import validate_station_exists, validate_train_exists
from typing import List
from datetime import datetime

router = APIRouter(
    prefix="/trains/{train_id}/stations",
    tags=["Stations"]
)

@router.get("/", response_model=List[StationUserResponse])
def get_stations(train_id: int):
    existing_train = trains_find_one(train_id)
    validate_train_exists(existing_train, train_id)

    existing_stations = stations.find()

    return existing_stations

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=StationAdminResponse)
def create_station(train_id: int, station: Station):
    try:
        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        station_id = get_next_sequence("station_id")
        station_data = {
            "train_id": train_id,
            "station_id": station_id,
            **station.dict(),
            "created_at": datetime.utcnow(),
            "updated_at": None,
            "is_deleted": False
        }

        result = stations.insert_one(station_data)
        created_station = stations.find_one({"_id": result.inserted_id})

        return created_station

    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/{station_id}", response_model=StationUserResponse)
def get_station(train_id: int, station_id: int):
    existing_train = trains_find_one(train_id)
    validate_train_exists(existing_train, train_id)

    existing_station = stations_find_one(train_id, station_id)
    validate_station_exists(existing_station, station_id)

    return existing_station

@router.put("/{station_id}", response_model=StationAdminResponse)
def put_station(train_id: int, station_id: int, station: StationPut):
    try:
        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        existing_station = stations_find_one(train_id, station_id)
        validate_station_exists(existing_station, station_id)

        station_data = station.dict()
        station_data["updated_at"] = datetime.utcnow()

        stations.update_one({"train_id": train_id, "station_id": station_id}, {"$set": station_data})
        updated_station = stations_find_one(train_id, station_id)

        return updated_station

    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/{station_id}", response_model=StationAdminResponse)
def patch_station(train_id: int, station_id: int, station: StationPatch):
    try:
        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        existing_station = stations_find_one(train_id, station_id)
        validate_station_exists(existing_station, station_id)

        station_data = station.dict(exclude_unset=True)
        station_data["updated_at"] = datetime.utcnow()

        stations.update_one({"train_id": train_id, "station_id": station_id}, {"$set": station_data})
        updated_station = stations_find_one(train_id, station_id)

        return updated_station

    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_station(train_id: int, station_id: int):
    try:
        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        existing_station = stations_find_one(train_id, station_id)
        validate_station_exists(existing_station, station_id)

        stations.delete_one({"train_id": train_id, "station_id": station_id})

        return
    
    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{station_id}/delete", status_code=status.HTTP_200_OK)
def soft_delete_station(train_id: int, station_id: int):
    try:
        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        existing_station = stations_find_one(train_id, station_id)
        validate_station_exists(existing_station, station_id)

        stations.update_one({"train_id": train_id, "station_id": station_id}, {"$set": {"is_deleted": True}})

        return {"Detail": f"Station with id {station_id} softly deleted"}
    
    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
