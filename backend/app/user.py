from ..utilities.models import ItemResponse, MyRequestsResponse
from ..db.repository import ItemRepository, UserRepository
from ..db.database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import APIRouter, Depends, Query
from typing import List

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