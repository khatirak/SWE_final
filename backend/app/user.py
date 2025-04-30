from ..utilities.models import ItemResponse, MyRequestsResponse
from ..db.repository import ItemRepository, UserRepository
from ..db.database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from typing import List, Dict
from pydantic import BaseModel

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

def get_item_repository(db = Depends(get_database)) -> ItemRepository:
    return ItemRepository(db)
def get_user_repository(db = Depends(get_database)) -> UserRepository:
    return UserRepository(db)

class PhoneUpdateRequest(BaseModel):
    phone: str

@router.get("/{user_id}/listings", response_model=List[ItemResponse])
async def get_my_listings(
    user_id: str,
    repo: ItemRepository = Depends(get_item_repository)
):
    return await repo.get_items_by_seller_id(user_id)

@router.get("/has_phone", response_model=Dict[str, bool])
async def check_has_phone(
    request: Request,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Check if the authenticated user has a phone number
    
    Args:
        request: HTTP request with session
        user_repo: User repository
        
    Returns:
        {"has_phone": true/false}
    """
    user = request.session.get('user')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user_data = await user_repo.get_user_by_id(user['id'])
    return {"has_phone": user_data.phone is not None and user_data.phone != ""}

@router.post("/update_phone", status_code=status.HTTP_200_OK)
async def update_phone(
    phone_data: PhoneUpdateRequest,
    request: Request,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Update authenticated user's phone number
    
    Args:
        phone_data: Phone update request with phone number
        request: HTTP request with session
        user_repo: User repository
        
    Returns:
        Success message
    """
    user = request.session.get('user')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    result = await user_repo.update_user_phone(user['id'], phone_data.phone)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Phone number updated successfully"}

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