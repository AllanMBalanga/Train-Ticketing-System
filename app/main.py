from fastapi import FastAPI
from .routers import users, balances, transactions, trains, stations, travels, payments

app = FastAPI()

app.include_router(users.router)
app.include_router(balances.router)
app.include_router(transactions.router)
app.include_router(trains.router)
app.include_router(stations.router)
app.include_router(travels.router)
app.include_router(payments.router)
#IF USING _id FOR PATH instead of table_id
#from bson import ObjectId
# def validate_object_id(id):
#     if not ObjectId.is_valid(id):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")
