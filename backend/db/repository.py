from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from backend.utilities.models import (
    UserCreate, UserResponse, ItemCreate, ItemResponse,
    ReservationCreate, ReservationResponse, ListingStatus, SearchFilters, ItemCategory, ReservationStatus, MyRequestsResponse
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
        item_dict["seller_id"] = ObjectId(seller_id)
        item_dict["created_at"] = datetime.now(timezone.utc)
        item_dict["status"] = ListingStatus.AVAILABLE
        item_dict["reservation_count"] = 0
        
        result = await self.collection.insert_one(item_dict)
        item_dict["id"] = str(result.inserted_id)
        item_dict["seller_id"] = str(item_dict["seller_id"])
        return ItemResponse(**item_dict)

    async def get_item(self, item_id: str) -> Optional[ItemResponse]:
        item = await self.collection.find_one({"_id": ObjectId(item_id)})
        if item:
            item["id"] = str(item["_id"])
            item["seller_id"] = str(item["seller_id"])
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
            result["seller_id"] = str(result["seller_id"])
            return ItemResponse(**result)
        return None
    
    async def update_status(self, item_id: str, new_status: ListingStatus) -> Optional[ItemResponse]:
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(item_id)},
            {"$set": {"status": new_status}},
            return_document=True
        )
        if result:
            result["id"] = str(result["_id"])
            result["seller_id"] = str(result["seller_id"])
            return ItemResponse(**result)
        return None

    async def delete_item(self, item_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0
    
    async def get_items_by_seller_id(self, seller_id: str) -> List[ItemResponse]:
        cursor = self.collection.find({"seller_id": ObjectId(seller_id)})
        listings = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            doc["seller_id"] = str(doc["seller_id"])
            listings.append(ItemResponse(**doc))
        return listings
    
    async def search_items(self, filters: SearchFilters) -> List[ItemResponse]:
        query = {}

        # Keyword-based search (title or description)
        if filters.keyword:
            query["$or"] = [
                {"title": {"$regex": filters.keyword, "$options": "i"}},
                {"description": {"$regex": filters.keyword, "$options": "i"}}
            ]

        # Category filter
        if filters.category:
            query["category"] = filters.category

        # Price range filter
        if filters.min_price is not None or filters.max_price is not None:
            query["price"] = {}
            if filters.min_price is not None:
                query["price"]["$gte"] = filters.min_price
            if filters.max_price is not None:
                query["price"]["$lte"] = filters.max_price

        # Condition filter
        if filters.condition:
            query["condition"] = filters.condition

        # Status filter
        if filters.status:
            query["status"] = filters.status

        # Tags filtering (match at least one tag)
        if filters.tags:
            query["tags"] = {"$in": filters.tags}

        # Sorting
        sort_field = filters.sort_by or "created_at"
        sort_order = ASCENDING if filters.sort_order == "asc" else DESCENDING

        # Execute query
        cursor = self.collection.find(query).sort(sort_field, sort_order)

        # Return results as ItemResponse
        results = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            doc["seller_id"] = str(doc["seller_id"])
            # doc["buyerId"] = str(doc["buyerId"])
            # print(doc)
            results.append(ItemResponse(**doc))

        return results

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

    async def add_reservation_request(self, listing_id: str, buyer_id: str) -> bool:
        now = datetime.now(timezone.utc)

        # Check if the user already has a reservation request for this listing
        listing = await self.collection.find_one({"_id": ObjectId(listing_id)})
        if not listing:
            return False

        # Avoid duplicate reservation requests
        for r in listing.get("reservation_requests", []):
            if str(r["buyer_id"]) == str(buyer_id):
                return False  # Already exists

        reservation_entry = {
            "buyer_id": ObjectId(buyer_id),
            "requested_at": now.isoformat(),
            "expires_at": (now + timedelta(days=7)).isoformat(),
            "status": ReservationStatus.PENDING
        }

        result = await self.collection.update_one(
            {"_id": ObjectId(listing_id)},
            {
                "$addToSet": {"reservation_requests": reservation_entry},
                "$inc": {"reservation_count": 1}
            }
        )
        return result.modified_count > 0

    async def confirm_reservation(self, listing_id: str, buyer_id: str) -> bool:
        listing = await self.collection.find_one({"_id": ObjectId(listing_id)})
        if not listing:
            return False

        updated_requests = []
        found = False

        for r in listing.get("reservation_requests", []):
            if str(r["buyer_id"]) == buyer_id:
                r["status"] = "confirmed"
                found = True
            updated_requests.append(r)

        if not found:
            return False  # Can't confirm if buyer isn't in the list

        result = await self.collection.update_one(
            {"_id": ObjectId(listing_id)},
            {
                "$set": {
                    "status": "reserved",
                    "buyerId": ObjectId(buyer_id),
                    "reservation_requests": updated_requests
                }
            }
        )
        return result.modified_count > 0

    async def get_reservations(self, listing_id: str, user_repo: UserRepository) -> Optional[List[dict]]:
        listing = await self.collection.find_one({"_id": ObjectId(listing_id)})
        if not listing:
            print("not found")
            return None

        now = datetime.now(timezone.utc)
        valid_reservations = []
        updated_requests = []

        # Safely interpret listing status as Enum
        listing_status = listing.get("status")
        if listing_status:
            listing_status = ListingStatus(listing_status)
        # print(listing_status)
        # If listing is reserved and has a confirmed buyer
        if listing_status == ListingStatus.RESERVED and listing.get("buyerId"):
            buyer_id = listing["buyerId"]
            # print(f"buyer id is {buyer_id}")

            # Use the UserRepository to get the user instance
            user = await user_repo.get_user_by_id(buyer_id)
            buyer_phone = user.phone if user else None

            # print(f"buyer phone is {buyer_phone}")

            for r in listing.get("reservation_requests", []):
                if r["buyer_id"] == buyer_id:
                    valid_reservations.append({
                        "buyer_id": str(r["buyer_id"]),
                        "requested_at": datetime.fromisoformat(r["requested_at"]),
                        "expires_at": datetime.fromisoformat(r["expires_at"]),
                        "status": "confirmed",
                        "buyer_phone": buyer_phone
                    })
                    break  # Only one confirmed reservation
        else:
            # Listing is available — return pending reservations
            for r in listing.get("reservation_requests", []):
                expires_at = datetime.fromisoformat(r["expires_at"])
                if now < expires_at:
                    valid_reservations.append({
                        "buyer_id": str(r["buyer_id"]),
                        "requested_at": datetime.fromisoformat(r["requested_at"]),
                        "expires_at": expires_at,
                        "status": "pending"
                    })
                    updated_requests.append(r)

            # Clean expired reservations
            if len(updated_requests) != len(listing.get("reservation_requests", [])):
                await self.collection.update_one(
                    {"_id": ObjectId(listing_id)},
                    {"$set": {"reservation_requests": updated_request,
                              "reservation_count": len(updated_request)}
                    }
                )

        return valid_reservations

    async def cancel_reservation(self, listing_id: str, buyer_id: str) -> bool:       
        listing = await self.collection.find_one({"_id": ObjectId(listing_id)})
        if not listing:
            return False

        # Safely interpret listing status as Enum
        listing_status = listing.get("status")
        if listing_status:
            listing_status = ListingStatus(listing_status)

        # For available listing, just delete the reservation (doesn't matter who initiated the cancellation)
        if listing_status == ListingStatus.AVAILABLE:
            result = await self.collection.update_one(
                {"_id": ObjectId(listing_id)},
                {
                "$pull": {"reservation_requests": {"buyer_id": ObjectId(buyer_id)}},
                "$inc": {"reservation_count": -1}
                }
            )
            return result.modified_count > 0
        else:
        # In case of reserved listing (change expiration date of the reservations left)
            now = datetime.now(timezone.utc)
            new_expiration = (now + timedelta(days=7)).isoformat()

            updated_requests = []
            for r in listing.get("reservation_requests", []):
                if str(r["buyer_id"]) == buyer_id:
                    continue
                r["expires_at"] = new_expiration
                updated_requests.append(r)

            result = await self.collection.update_one(
                {"_id": ObjectId(listing_id)},
                {
                    "$set": {
                        "status": "available",
                        "buyerId": None,
                        "reservation_requests": updated_requests
                    },
                    "$inc": {"reservation_count": -1}
                }
            )
            return result.modified_count > 0

    async def get_categories(self) -> List[str]:
        """
        Get all distinct categories from the database
        
        Returns:
            List of category names
        """
        # Get distinct categories from the listings collection
        categories = await self.collection.distinct("category")
        return categories

    async def mark_item_as_sold(self, listing_id: str) -> bool:
        """
        Mark a listing as sold and remove all reservation requests.
        """
        result = await self.collection.update_one(
            {"_id": ObjectId(listing_id)},
            {
                "$set": {
                    "status": ListingStatus.SOLD,
                    "reservation_requests": [],
                }
            }
        )
        return result.modified_count > 0
    
    async def get_items_by_seller_id(self, seller_id: str) -> List[ItemResponse]:
        cursor = self.collection.find({"seller_id": ObjectId(seller_id)})
        listings = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            doc["seller_id"] = str(doc["seller_id"])
            listings.append(ItemResponse(**doc))
        return listings

    async def get_items_requested_by_user(self, buyer_id: str, user_repo: "UserRepository") -> List[MyRequestsResponse]:
        cursor = self.collection.find({
            "reservation_requests.buyer_id": ObjectId(buyer_id)
        })

        results = []
        async for doc in cursor:
            seller_phone = None

            # Find the reservation that matches
            for r in doc.get("reservation_requests", []):
                if str(r["buyer_id"]) == buyer_id:
                    # Only fetch seller's phone if the reservation is confirmed
                    if r["status"] == "confirmed":
                        seller = await user_repo.get_user_by_id(str(doc["seller_id"]))
                        seller_phone = seller.phone if seller else None
                        
                        results.append(MyRequestsResponse(
                            listing_id=str(doc["_id"]),
                            title=doc["title"],
                            seller_id=str(doc["seller_id"]),
                            requested_at=datetime.fromisoformat(r["requested_at"]),
                            status=r["status"],
                            seller_phone=seller_phone
                        ))
                    else:
                        results.append(MyRequestsResponse(
                            listing_id=str(doc["_id"]),
                            title=doc["title"],
                            seller_id=str(doc["seller_id"]),
                            requested_at=datetime.fromisoformat(r["requested_at"]),
                            expires_at=datetime.fromisoformat(r["expires_at"]),
                            status=r["status"]
                        ))
                    break  # Only one reservation per listing

        return results


