from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from ..utilities.models import (
    UserCreate, UserResponse, ItemCreate, ItemResponse,
    ReservationCreate, ReservationResponse, ListingStatus
)

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    async def create_user(self, user: UserCreate) -> UserResponse:
        user_dict = user.dict()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["listings"] = []
        
        result = await self.collection.insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)
        return UserResponse(**user_dict)

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        user = await self.collection.find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])
            return UserResponse(**user)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["id"] = str(user["_id"])
            return UserResponse(**user)
        return None

class ItemRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.items

    async def create_item(self, item: ItemCreate, seller_id: str) -> ItemResponse:
        item_dict = item.dict()
        item_dict["seller_id"] = seller_id
        item_dict["created_at"] = datetime.utcnow()
        item_dict["status"] = ListingStatus.AVAILABLE
        item_dict["reservation_count"] = 0
        
        result = await self.collection.insert_one(item_dict)
        item_dict["id"] = str(result.inserted_id)
        return ItemResponse(**item_dict)

    async def get_item(self, item_id: str) -> Optional[ItemResponse]:
        item = await self.collection.find_one({"_id": ObjectId(item_id)})
        if item:
            item["id"] = str(item["_id"])
            return ItemResponse(**item)
        return None

    async def update_item(self, item_id: str, item_update: dict) -> Optional[ItemResponse]:
        item_update["updated_at"] = datetime.utcnow()
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(item_id)},
            {"$set": item_update},
            return_document=True
        )
        if result:
            result["id"] = str(result["_id"])
            return ItemResponse(**result)
        return None

    async def delete_item(self, item_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0

class ReservationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.reservations

    async def create_reservation(self, reservation: ReservationCreate) -> ReservationResponse:
        reservation_dict = reservation.dict()
        reservation_dict["created_at"] = datetime.utcnow()
        reservation_dict["status"] = "pending"
        
        result = await self.collection.insert_one(reservation_dict)
        reservation_dict["id"] = str(result.inserted_id)
        return ReservationResponse(**reservation_dict)

    async def get_reservation(self, reservation_id: str) -> Optional[ReservationResponse]:
        reservation = await self.collection.find_one({"_id": ObjectId(reservation_id)})
        if reservation:
            reservation["id"] = str(reservation["_id"])
            return ReservationResponse(**reservation)
        return None

    async def update_reservation_status(self, reservation_id: str, status: str) -> Optional[ReservationResponse]:
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(reservation_id)},
            {"$set": {"status": status}},
            return_document=True
        )
        if result:
            result["id"] = str(result["_id"])
            return ReservationResponse(**result)
        return None 