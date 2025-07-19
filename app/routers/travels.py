from fastapi import APIRouter, status, HTTPException
from ..body import Travel, get_next_sequence
from ..updates import TravelPut, TravelPatch
from ..response import TravelAdminResponse, TravelResponse
from ..queries import travels_find_one, travels, stations, trains_find_one, stations_find_one, travels_delete_one, travels_update_one, travels_find
from ..status_codes import validate_travel_exists, validate_station_exists, validate_train_exists
from typing import List
from datetime import datetime

router = APIRouter(
    prefix="/trains/{train_id}/travels",
    tags=["Travels"]
)

BASE_FARE = 13
PER_STATION_RATE = 1.3

travels.create_index("travel_id", unique=True)

@router.get("/", response_model=List[TravelResponse])
def get_travels(train_id: int):
    existing_train = trains_find_one(train_id)
    validate_train_exists(existing_train, train_id)
    
    travel = travels_find(train_id)

    return travel

@router.post("/", response_model=TravelResponse)
def create_travels(train_id: int, travel: Travel):
    try:
        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        departure_station = stations_find_one(train_id, travel.departure_id)
        validate_station_exists(departure_station, travel.departure_id)

        arrival_station = stations_find_one(train_id, travel.arrival_id)
        validate_station_exists(arrival_station, travel.arrival_id)

        #fare calculation
        number_of_positions = abs(departure_station["position"] - arrival_station["position"])
        total_fare = BASE_FARE + (number_of_positions * PER_STATION_RATE)
        
        travel_id = get_next_sequence("travel_id")
        travel_data = {
            "train_id": train_id,
            "travel_id": travel_id,
            **travel.dict(),
            "total": total_fare,
            "created_at": datetime.utcnow(),
            "updated_at": None,
            "is_deleted": False
        }

        result = travels.insert_one(travel_data)
        created_travel = travels.find_one({"_id": result.inserted_id})

        return created_travel
        
    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/{travel_id}", response_model=TravelResponse)
def get_travel(train_id: int, travel_id: int):
    existing_train = trains_find_one(train_id)
    validate_train_exists(existing_train, train_id)

    existing_travel = travels_find_one(train_id, travel_id)
    validate_travel_exists(existing_travel, travel_id)

    return existing_travel

@router.put("/{travel_id}", response_model=TravelResponse)
def put_travel(train_id: int, travel_id: int, travel: TravelPut):
    try:
        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        existing_travel = travels_find_one(train_id, travel_id)
        validate_travel_exists(existing_travel, travel_id)

        departure_station = stations_find_one(train_id, travel.departure_id)
        arrival_station = stations_find_one(train_id, travel.arrival_id)
        validate_station_exists(departure_station, travel.departure_id)
        validate_station_exists(arrival_station, travel.arrival_id)

        number_of_positions = abs(departure_station["position"] - arrival_station["position"])
        total_fare = BASE_FARE + (number_of_positions * PER_STATION_RATE)

        travel_data = {
            **travel.dict(),
            "total": total_fare,
            "updated_at": datetime.utcnow(),
        }

        travels_update_one(train_id, travel_id, travel_data)
        updated_travel = travels.find_one({"train_id": train_id, "travel_id": travel_id})

        return updated_travel
    
    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.patch("/{travel_id}", response_model=TravelResponse)
def patch_travel(train_id: int, travel_id: int, travel: TravelPatch):
    try:
        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        existing_travel = travels_find_one(train_id, travel_id)
        validate_travel_exists(existing_travel, travel_id)

        travel_updates = travel.dict(exclude_unset=True)

        if "departure_id" in travel_updates or "arrival_id" in travel_updates:
            #dict.get(key, default_value) - If key exists → return its value, If key doesn’t exist → return default_value instead
            dep_id = travel_updates.get("departure_id", existing_travel["departure_id"])
            arr_id = travel_updates.get("arrival_id", existing_travel["arrival_id"])
            
            departure_station = stations_find_one(train_id, dep_id)
            arrival_station = stations_find_one(train_id, arr_id)
            validate_station_exists(departure_station, dep_id)
            validate_station_exists(arrival_station, arr_id)

            number_of_positions = abs(departure_station["position"] - arrival_station["position"])
            total_fare = BASE_FARE + (number_of_positions * PER_STATION_RATE)
        else:
            total_fare = existing_travel["total"]

        travel_data = {
            **travel_updates,
            "total": total_fare,
            "updated_at": datetime.utcnow(),
        }

        travels_update_one(train_id, travel_id, travel_data)
        updated_travel = travels_find_one(train_id, travel_id)

        return updated_travel
    
    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{travel_id}", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_travel(train_id: int, travel_id: int):
    try:
        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        existing_travel = travels_find_one(train_id, travel_id)
        validate_travel_exists(existing_travel, travel_id)

        travels_delete_one(train_id, travel_id)

        return

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.delete("/{travel_id}/delete", status_code=status.HTTP_200_OK)
def soft_delete_travel(train_id: int, travel_id: int):
    try:
        existing_train = trains_find_one(train_id)
        validate_train_exists(existing_train, train_id)

        existing_travel = travels_find_one(train_id, travel_id)
        validate_travel_exists(existing_travel, travel_id)

        travels_update_one(train_id, travel_id, {"is_deleted": True})

        return {"Detail": f"Travel with id {travel_id} softly deleted"}

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
