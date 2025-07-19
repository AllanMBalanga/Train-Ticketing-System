from fastapi import status, APIRouter, HTTPException, Depends
from ..body import Station, get_next_sequence, TokenData
from ..updates import StationPatch, StationPut
from ..response import StationAdminResponse, StationResponse
from ..queries import stations, stations_find_one, trains_find_one, stations_update_one, stations_delete_one, stations_find
from ..status_codes import validate_station_exists, validate_train_exists, validate_required_roles
from typing import List, Union
from datetime import datetime
from ..oauth2 import get_current_user

router = APIRouter(
    prefix="/trains/{train_id}/stations",
    tags=["Stations"]
)

stations.create_index("station_id", unique=True)

@router.get("/", response_model=List[Union[StationResponse, StationAdminResponse]])
def get_stations(train_id: int, current_user: TokenData = Depends(get_current_user)):
    validate_required_roles(current_user.role, ["user", "admin"])

    existing_train = trains_find_one(train_id)
    validate_train_exists(existing_train, train_id)

    existing_stations = stations_find(train_id)

    if current_user.role == "user":
        return [StationResponse(**i) for i in existing_stations]
    else:
        return [StationAdminResponse(**i) for i in existing_stations]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=StationAdminResponse)
def create_station(train_id: int, station: Station, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

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

@router.get("/{station_id}", response_model=Union[StationResponse, StationAdminResponse])
def get_station(train_id: int, station_id: int, current_user: TokenData = Depends(get_current_user)):
    validate_required_roles(current_user.role, ["user", "admin"])

    existing_train = trains_find_one(train_id)
    validate_train_exists(existing_train, train_id)

    existing_station = stations_find_one(train_id, station_id)
    validate_station_exists(existing_station, station_id)

    if current_user.role == "user":
        return StationResponse(**existing_station)
    else:
        return StationAdminResponse(**existing_station)

@router.put("/{station_id}", response_model=StationAdminResponse)
def put_station(train_id: int, station_id: int, station: StationPut, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        existing_station = stations_find_one(train_id, station_id)
        validate_station_exists(existing_station, station_id)

        station_data = station.dict()
        station_data["updated_at"] = datetime.utcnow()

        stations_update_one(train_id, station_id, station_data)
        updated_station = stations_find_one(train_id, station_id)

        return updated_station

    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/{station_id}", response_model=StationAdminResponse)
def patch_station(train_id: int, station_id: int, station: StationPatch, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        existing_station = stations_find_one(train_id, station_id)
        validate_station_exists(existing_station, station_id)

        station_data = station.dict(exclude_unset=True)
        station_data["updated_at"] = datetime.utcnow()

        stations_update_one(train_id, station_id, station_data)
        updated_station = stations_find_one(train_id, station_id)

        return updated_station

    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_station(train_id: int, station_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        existing_station = stations_find_one(train_id, station_id)
        validate_station_exists(existing_station, station_id)

        stations_delete_one(train_id, station_id)

        return
    
    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{station_id}/delete", status_code=status.HTTP_200_OK)
def soft_delete_station(train_id: int, station_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        validate_required_roles(current_user.role, ["admin"])

        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        existing_station = stations_find_one(train_id, station_id)
        validate_station_exists(existing_station, station_id)

        stations_update_one(train_id, station_id, {"is_deleted": True})

        return {"detail": f"Station with id {station_id} softly deleted"}
    
    except HTTPException:
        raise 

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
