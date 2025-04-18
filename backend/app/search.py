from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from utilities.models import ItemResponse, SearchFilters, ItemCategory, ItemCondition, ListingStatus
from db.repository import ItemRepository
from db.database import get_database

router = APIRouter(
    prefix="/search",
    tags=["search"],
)

def get_item_repository(db = Depends(get_database)) -> ItemRepository:
    return ItemRepository(db)

@router.get("/", response_model=List[ItemResponse])
async def search_items(
    keyword: Optional[str] = None,
    category: Optional[ItemCategory] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    condition: Optional[ItemCondition] = None,
    status: Optional[ListingStatus] = ListingStatus.AVAILABLE,
    tags: Optional[List[str]] = Query(None),
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: ItemRepository = Depends(get_item_repository)
):
    """
    Search for items with filters [R-201, R-202, R-203, R-204]
    
    This endpoint processes search queries within 3 seconds and supports:
    - Keyword-based search
    - Price range filtering
    - Category filtering
    - Date-based filtering
    - Condition filtering
    - Status filtering
    - Tag filtering
    - Sorting options
    
    Args:
        keyword: Search term for title and description
        category: Filter by category
        min_price: Minimum price
        max_price: Maximum price
        condition: Filter by condition
        status: Filter by listing status
        tags: Filter by tags
        sort_by: Field to sort by
        sort_order: Sort direction (asc/desc)
        db: Database connection
        
    Returns:
        List of items matching search criteria
    """
    filters = SearchFilters(
        keyword=keyword,
        category=category,
        min_price=min_price,
        max_price=max_price,
        condition=condition,
        status=status,
        tags=tags,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return await repo.search_items(filters)

@router.get("/categories", response_model=List[str])
async def get_categories(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all available categories
    
    Args:
        db: Database connection
        
    Returns:
        List of categories
    """
    # Implementation placeholder
    pass

@router.get("/popular-tags", response_model=List[str])
async def get_popular_tags(
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get popular tags
    
    Args:
        limit: Maximum number of tags to return
        db: Database connection
        
    Returns:
        List of popular tags
    """
    # Implementation placeholder
    pass

@router.post("/save-preferences", status_code=201)
async def save_search_preferences(
    filters: SearchFilters,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Save user search preferences [R-205]
    
    Args:
        filters: Search filters to save
        db: Database connection
        
    Returns:
        Confirmation message
    """
    # Implementation placeholder
    pass
