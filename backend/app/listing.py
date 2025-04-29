from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..utilities.models import ItemCreate, ItemResponse, ItemUpdate, ListingStatus
from ..utilities.models import ReservationCreate, ReservationConfirmation, ReservationInfo
from fastapi import HTTPException
from ..db.repository import ItemRepository, UserRepository
from ..db.database import get_database

router = APIRouter(
    prefix="/listings",
    tags=["listings"],
)

def get_item_repository(db = Depends(get_database)) -> ItemRepository:
    return ItemRepository(db)

def get_user_repository(db = Depends(get_database)) -> UserRepository:
    return UserRepository(db)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    item: ItemCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: ItemRepository = Depends(get_item_repository)
):
    """
    Create a new item listing [R-101, R-102, R-103, R-104, R-105, R-106, R-107]
    
    This endpoint allows users to create a new listing with all required details:
    - Title (max 100 characters)
    - Description (max 200 words)
    - Price (zero or positive)
    - Category (from predefined list)
    - Condition (from predefined list)
    - Images (2-10 images, each <5MB)
    
    Args:
        item: Item details
        db: Database connection
        
    Returns:
        Created item with ID and timestamps
    """
    return await repo.create_item(item, seller_id="100") #seller_id???
    

@router.get("/{item_id}", response_model=ItemResponse)
async def get_listing(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: ItemRepository = Depends(get_item_repository)
):
    """
    Get details for a specific listing
    
    Args:
        item_id: ID of the item
        db: Database connection
        
    Returns:
        Item details
    """
    # Implementation placeholder
    return await repo.get_item(item_id)

@router.put("/{item_id}", response_model=ItemResponse)
async def update_listing(
    item_id: str,
    item: ItemUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: ItemRepository = Depends(get_item_repository)
):
    """
    Update an existing listing
    
    Args:
        item_id: ID of the item to update
        item: Updated item details
        db: Database connection
        
    Returns:
        Updated item
    """
    # Implementation placeholder
    return await repo.update_item(item_id, item.dict(exclude_unset=True))

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: ItemRepository = Depends(get_item_repository)
):
    """
    Delete a listing
    
    Args:
        item_id: ID of the item to delete
        db: Database connection
    """
    # Implementation placeholder
    return await repo.delete_item(item_id)

@router.post("/{item_id}/images", response_model=ItemResponse)
async def upload_images(
    item_id: str,
    files: List[UploadFile] = File(...),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Upload images for a listing [R-106, R-107]
    
    Args:
        item_id: ID of the item
        files: Image files to upload (2-10 images, each <5MB)
        db: Database connection
        
    Returns:
        Updated item with image URLs
    """
    # Implementation placeholder
    pass

@router.put("/{item_id}/status", response_model=ItemResponse)
async def update_listing_status(
    item_id: str,
    status: ListingStatus,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update listing status (Available, Reserved, Sold) [R-304]
    
    Args:
        item_id: ID of the item
        status: New status
        db: Database connection
        
    Returns:
        Updated item with new status
    """
    # Implementation placeholder
    pass



# POST: Create a reservation request
@router.post("/{item_id}/request", status_code=200)
async def request_reservation(
    item_id: str,
    reservation: ReservationCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: ItemRepository = Depends(get_item_repository)
):
    """
    Request to reserve an item.
    """
    success = await repo.add_reservation_request(item_id, reservation.buyer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Listing not found or reservation failed")
    return {"message": "Reservation request submitted successfully."}

# POST: Confirm a reservation request
@router.post("/{item_id}/confirm", status_code=200)
async def confirm_reservation(
    item_id: str,
    confirmation: ReservationConfirmation,
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: ItemRepository = Depends(get_item_repository)
):
    """
    Confirm a reservation request for a listing.
    """
    success = await repo.confirm_reservation(item_id, confirmation.buyer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Listing not found or confirmation failed")
    return {"message": "Reservation confirmed successfully."}

@router.get("/{item_id}/reservations", response_model=List[ReservationInfo], status_code=200)
async def get_reservations(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: ItemRepository = Depends(get_item_repository),
    user_repo: ItemRepository = Depends(get_user_repository)
):
    """
    Get all reservation requests for a listing.
    """
    reservations = await repo.get_reservations(item_id, user_repo)
    if reservations is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return reservations

@router.delete("/{item_id}/cancel_reservation", status_code=200)
async def cancel_reservation_request(
    item_id: str,
    buyer_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: ItemRepository = Depends(get_item_repository)
):
    success = await repo.cancel_reservation(item_id, buyer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reservation not found or listing not found")
    return {"message": "Reservation request cancelled successfully."}

@router.post("/{item_id}/sold", status_code=200)
async def mark_listing_as_sold(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: ItemRepository = Depends(get_item_repository)
):
    """
    Mark a listing as sold and clear reservations.
    """
    success = await repo.mark_item_as_sold(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"message": "Listing marked as sold successfully."}

@router.get("/user/{user_id}", response_model=List[ItemResponse])
async def get_user_listings(
    user_id: str,
    status: Optional[ListingStatus] = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: ItemRepository = Depends(get_item_repository)
):
    """
    Get all listings for a specific user
    
    Args:
        user_id: ID of the user
        status: Filter by listing status
        db: Database connection
        
    Returns:
        List of user's listings
    """
    # Implementation placeholder
    return await repo.get_items_by_seller_id(user_id)
