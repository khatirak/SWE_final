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
        user_dict = user.model_dump()
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
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                # Ensure required fields exist in the response
                if "phone" not in user:
                    user["phone"] = None
                if "listings" not in user:
                    user["listings"] = []
                return UserResponse(**user)
            return None
        except Exception as e:
            # Handle invalid ObjectId or other database errors
            print(f"Error getting user by ID: {str(e)}")
            return None

    async def update_phone(self, user_id: str, phone_number: str) -> bool:
        """
        Update user's phone number
        
        Args:
            user_id: ID of the user
            phone_number: New phone number
            
        Returns:
            True if successfully updated, False otherwise
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"phone": phone_number}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating phone number: {str(e)}")
            return False

class ItemRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.Listings

    async def create_item(self, item: ItemCreate, seller_id: str) -> ItemResponse:
        item_dict = item.model_dump()
        item_dict["seller_id"] = ObjectId(seller_id)
        item_dict["created_at"] = datetime.now(timezone.utc)
        item_dict["status"] = ListingStatus.AVAILABLE
        item_dict["reservation_count"] = 0
        item_dict["reservation_requests"] = []  # Initialize empty array
        
        result = await self.collection.insert_one(item_dict)
        item_dict["id"] = str(result.inserted_id)
        item_dict["seller_id"] = str(item_dict["seller_id"])
        return ItemResponse(**item_dict)

    async def get_item(self, item_id: str) -> Optional[ItemResponse]:
        item = await self.collection.find_one({"_id": ObjectId(item_id)})
        if item:
            item["id"] = str(item["_id"])
            item["seller_id"] = str(item["seller_id"])
            
            # Convert buyerId to string if present
            if "buyerId" in item and item["buyerId"] is not None:
                item["buyerId"] = str(item["buyerId"])
                
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
            
            # Convert buyerId to string if present
            if "buyerId" in result and result["buyerId"] is not None:
                result["buyerId"] = str(result["buyerId"])
                
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
            
            # Convert buyerId to string if present
            if "buyerId" in result and result["buyerId"] is not None:
                result["buyerId"] = str(result["buyerId"])
                
            return ItemResponse(**result)
        return None

    async def delete_item(self, item_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0
    
    async def get_items_by_seller_id(self, seller_id: str) -> List[ItemResponse]:
        count = await self.db.Listings.count_documents({})
        cursor = self.collection.find({"seller_id": ObjectId(seller_id)})
        listings = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            doc["seller_id"] = str(doc["seller_id"])
            
            # Convert buyerId to string if present
            if "buyerId" in doc and doc["buyerId"] is not None:
                doc["buyerId"] = str(doc["buyerId"])
                
            listings.append(ItemResponse(**doc))
        return listings
    
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
            doc["seller_id"] = str(doc["seller_id"])
            
            # Convert buyerId to string if present
            if "buyerId" in doc and doc["buyerId"] is not None:
                doc["buyerId"] = str(doc["buyerId"])
                
            listings.append(ItemResponse(**doc))

        return listings

    async def add_reservation_request(self, listing_id: str, buyer_id: str) -> bool:
        print(f"Adding reservation request: listing={listing_id}, buyer={buyer_id}")
        now = datetime.now(timezone.utc)

        # Check if the user already has a reservation request for this listing
        listing = await self.collection.find_one({"_id": ObjectId(listing_id)})
        if not listing:
            print("Listing not found")
            return False
            
        # Initialize reservation_requests if it doesn't exist
        reservation_requests = listing.get("reservation_requests", [])
        
        # Check for duplicate requests
        for r in reservation_requests:
            stored_buyer_id = str(r["buyer_id"]) if isinstance(r["buyer_id"], ObjectId) else r["buyer_id"]
            if stored_buyer_id == str(buyer_id):
                print(f"Request already exists for buyer {buyer_id}")
                return False  # Already exists

        # Create the new reservation entry
        reservation_entry = {
            "buyer_id": ObjectId(buyer_id),
            "requested_at": now.isoformat(),
            "expires_at": (now + timedelta(days=7)).isoformat(),
            "status": ReservationStatus.PENDING
        }
        
        # Determine the current count for increment
        current_count = listing.get("reservation_count", 0)
        
        # Update the listing with the new request
        result = await self.collection.update_one(
            {"_id": ObjectId(listing_id)},
            {
                "$push": {"reservation_requests": reservation_entry},
                "$set": {"reservation_count": current_count + 1}
            }
        )
        
        print(f"Added reservation request: modified_count={result.modified_count}")
        return result.modified_count > 0

    async def confirm_reservation(self, listing_id: str, buyer_id: str) -> bool:
        print(f"Confirming reservation: listing={listing_id}, buyer={buyer_id}")
        
        # Get the current listing
        listing = await self.collection.find_one({"_id": ObjectId(listing_id)})
        if not listing:
            print("Listing not found")
            return False

        updated_requests = []
        found = False
        
        # Convert buyer_id to ObjectId if it's not already
        try:
            buyer_obj_id = ObjectId(buyer_id)
        except:
            print(f"Invalid buyer_id format: {buyer_id}")
            return False

        # Check if we have any reservation requests
        if not listing.get("reservation_requests"):
            return False
        else:
            # Process existing requests
            for r in listing.get("reservation_requests", []):
                # Convert stored buyer_id to string for comparison
                r_buyer_id = str(r["buyer_id"])
                if r_buyer_id == buyer_id:
                    print(f"Found matching request for buyer {buyer_id}")
                    r["status"] = "confirmed"
                    found = True
                updated_requests.append(r)

        if not found:
            print(f"No matching reservation request found for buyer {buyer_id}")
            # If we didn't find the buyer return error
            return False

        # Update the listing with the new status and reservation data
        result = await self.collection.update_one(
            {"_id": ObjectId(listing_id)},
            {
                "$set": {
                    "status": "reserved",
                    "buyerId": str(buyer_obj_id),
                    "reservation_requests": updated_requests,
                    "reservation_count": len(updated_requests)
                }
            }
        )
        print(f"Updated listing result: modified_count={result.modified_count}")
        return result.modified_count > 0

    async def get_reservations(self, listing_id: str, user_repo: UserRepository) -> Optional[List[dict]]:
        listing = await self.collection.find_one({"_id": ObjectId(listing_id)})
        if not listing:
            print("Listing not found")
            return []  # Return empty list instead of None

        now = datetime.now(timezone.utc)
        valid_reservations = []
        updated_requests = []

        # Safely interpret listing status as Enum
        listing_status = listing.get("status")
        if listing_status:
            listing_status = ListingStatus(listing_status)
        
        # Debug the listing data
        print(f"Listing ID: {listing_id}, Status: {listing_status}")
        print(f"Reservation count: {listing.get('reservation_count', 0)}")
        print(f"Reservation requests: {listing.get('reservation_requests', [])}")
        print(f"Buyer ID: {listing.get('buyerId')}")

        # If listing is reserved and has a confirmed buyer
        if listing_status == ListingStatus.RESERVED and listing.get("buyerId"):
            buyer_id = listing["buyerId"]
            print(f"Processing confirmed reservation for buyer: {buyer_id}")

            # Use the UserRepository to get the user instance
            user = await user_repo.get_user_by_id(str(buyer_id))
            buyer_phone = user.phone if user else None

            # Check if there's a reservation request for this buyer
            found_request = False
            for r in listing.get("reservation_requests", []):
                if str(r["buyer_id"]) == str(buyer_id):
                    found_request = True
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
                    {"$set": {"reservation_requests": updated_requests,
                              "reservation_count": len(updated_requests)}
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

        requests = listing.get("reservation_requests", [])
        
        # if buyer never requested, fail early
        if not any(str(r["buyer_id"]) == buyer_id for r in requests):
            return False
        
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
            request_exists = False
            for r in requests:
                if str(r["buyer_id"]) == buyer_id:
                    request_exists = True
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
            return result.modified_count > 0 and request_exists

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
                    "reservation_count": 0
                }
            }
        )
        return result.modified_count > 0

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

    async def get_reservation_request(self, user_id: str, user_repo: "UserRepository", item_id: str) -> List[MyRequestsResponse]:
        doc = await self.collection.find_one({"_id": ObjectId(item_id)})
        if not doc:
            return []

        for r in doc.get("reservation_requests", []):
            if str(r["buyer_id"]) == user_id:
                seller_phone = None
                if r["status"] == "confirmed":
                    seller = await user_repo.get_user_by_id(str(doc["seller_id"]))
                    seller_phone = seller.phone if seller else None

                response = MyRequestsResponse(
                    listing_id=str(doc["_id"]),
                    title=doc["title"],
                    seller_id=str(doc["seller_id"]),
                    requested_at=datetime.fromisoformat(r["requested_at"]),
                    status=r["status"],
                    seller_phone=seller_phone
                )

                if r["status"] != "confirmed":
                    response.expires_at = datetime.fromisoformat(r["expires_at"])

                return [response]

        return []