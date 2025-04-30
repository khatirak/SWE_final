from ..utilities.models import ItemResponse, MyRequestsResponse
from ..db.repository import ItemRepository, UserRepository
from ..db.database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from typing import List
from pydantic import BaseModel

# Model for phone update
class PhoneUpdate(BaseModel):
    phoneNumber: str

# Create two separate routers
router = APIRouter(
    prefix="/user",
    tags=["user"],
)

def get_item_repository(db = Depends(get_database)) -> ItemRepository:
    return ItemRepository(db)
def get_user_repository(db = Depends(get_database)) -> UserRepository:
    return UserRepository(db)

@router.get("/{user_id}/listings", response_model=List[ItemResponse])
async def get_my_listings(
    user_id: str,
    repo: ItemRepository = Depends(get_item_repository)
):
    return await repo.get_items_by_seller_id(user_id)


@router.get("/{user_id}/my_requests", response_model=List[MyRequestsResponse])
async def get_my_requests(
    user_id: str,
    repo: ItemRepository = Depends(get_item_repository),
    user_repo: UserRepository = Depends(get_user_repository)
):
    return await repo.get_items_requested_by_user(user_id, user_repo)

@router.get("/{user_id}/my_requests/{item_id}", response_model=List[MyRequestsResponse])
async def get_my_requests(
    user_id: str,
    item_id: str,
    repo: ItemRepository = Depends(get_item_repository),
    user_repo: UserRepository = Depends(get_user_repository)
):
    return await repo.get_reservation_request(user_id, user_repo, item_id)

# Add the update-phone endpoint 
@router.post("/update-phone")
async def update_phone(
    phone_data: PhoneUpdate,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update user's phone number
    
    Args:
        phone_data: The phone number to update
        request: HTTP request with session
        db: Database connection
        
    Returns:
        Success message
    """
    user = request.session.get('user')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Update phone number in database
    user_repo = UserRepository(db)
    success = await user_repo.update_phone(user['id'], phone_data.phoneNumber)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or update failed"
        )
    
    return {"message": "Phone number updated successfully"}