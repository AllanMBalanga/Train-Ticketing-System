from fastapi import FastAPI
from .routers import users

app = FastAPI()

app.include_router(users.router)

#IF USING _id FOR PATH instead of table_id
#from bson import ObjectId
# def validate_object_id(id):
#     if not ObjectId.is_valid(id):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")
