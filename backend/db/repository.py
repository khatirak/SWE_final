from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pymongo import ASCENDING, DESCENDING

from utilities.models import (
    UserCreate, UserResponse, ItemCreate, ItemResponse,
    ReservationCreate, ReservationResponse, ListingStatus, SearchFilters, ItemCategory
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
        self.collection = db.Listings

    async def create_item(self, item: ItemCreate, seller_id: str) -> ItemResponse:
        item_dict = item.dict()
        item_dict["seller_id"] = seller_id
        item_dict["created_at"] = datetime.now(timezone.utc)
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
        item_update["updated_at"] = datetime.now(timezone.utc)
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
    
    async def get_items_by_seller_id(self, seller_id: str) -> List[ItemResponse]:
        cursor = self.collection.find({"seller_id": seller_id})
        listings = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            listings.append(ItemResponse(**doc))
        return listings
    
    async def search_items(self, filter_dict: dict, sort_dict: dict, skip: int = 0, limit: int = 20) -> List[ItemResponse]:
        """
        Search for items based on filter criteria
        
        Args:
            filter_dict: Dictionary of filter criteria
            sort_dict: Dictionary of sort criteria
            skip: Number of items to skip (for pagination)
            limit: Maximum number of items to return
            
        Returns:
            List of matching items
        """
        cursor = self.collection.find(filter_dict)
        
        # Apply sorting
        if sort_dict:
            cursor = cursor.sort(list(sort_dict.items()))
        
        # Apply pagination
        cursor = cursor.skip(skip).limit(limit)
        
        # Return results as ItemResponse
        results = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            results.append(ItemResponse(**doc))
        
        return results
    
    async def get_categories(self) -> List[str]:
        """
        Get all distinct categories from the database
        
        Returns:
            List of category names
        """
        # Get distinct categories from the listings collection
        categories = await self.collection.distinct("category")
        return categories
    
    async def get_recent(self, limit: int = 10, category: Optional[ItemCategory] = None) -> List[ItemResponse]:
        query = {}

        if category:
            query["category"] = category

        cursor = (
            self.collection
            .find(query)
            .sort("created_at", -1)  # descending order
            .limit(limit)
        )

        listings = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            listings.append(ItemResponse(**doc))

        return listings

class ReservationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.reservations

    async def create_reservation(self, reservation: ReservationCreate) -> ReservationResponse:
        reservation_dict = reservation.dict()
        reservation_dict["created_at"] = datetime.now(timezone.utc)
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
    
   