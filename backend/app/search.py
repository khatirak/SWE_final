# backend/app/search.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
import logging
import re

from utilities.models import ItemResponse, SearchFilters, ItemCategory, ItemCondition, ListingStatus
from db.repository import ItemRepository
from db.database import get_database

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/search",
    tags=["search"],
)

def get_item_repository(db = Depends(get_database)) -> ItemRepository:
    return ItemRepository(db)

@router.get("", include_in_schema=False)
async def redirect_to_search():
    """
    Redirect requests without trailing slash to the endpoint with trailing slash
    """
    return RedirectResponse(url="/search/")

@router.get("/", response_model=List[ItemResponse])
async def search_listings(
    q: Optional[str] = Query(None, description="Search query for title and description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    status: Optional[str] = Query(None, description="Filter by status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    location: Optional[str] = Query(None, description="Filter by location"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[int] = Query(-1, description="Sort order: 1 for ascending, -1 for descending"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Create a filter dictionary
    filter_dict = {}
    
    logger.info(f"Search parameters - Query: {q}, Category: {category}, Status: {status}")
    
    # Add search query filter (search in title and description)
    if q:
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}}
        ]
    
    # Add other filters
    if category:
        # Convert spaces to underscores and make case-insensitive
        category_normalized = category.lower().replace(" ", "_")
        filter_dict["category"] = {"$regex": f"^{category_normalized}$", "$options": "i"}
    
    if condition:
        filter_dict["condition"] = {"$regex": condition, "$options": "i"}
    
    if status:
        # Make status case-insensitive
        filter_dict["status"] = {"$regex": f"^{status}$", "$options": "i"}
    else:
        # Default to showing only available items (case-insensitive)
        filter_dict["status"] = {"$regex": "^available$", "$options": "i"}
    
    # Price range filter
    price_filter = {}
    if min_price is not None:
        price_filter["$gte"] = min_price
    if max_price is not None:
        price_filter["$lte"] = max_price
    if price_filter:
        filter_dict["price"] = price_filter
    
    # Create sort dict - default to sorting by creation date, newest first
    sort_dict = {sort_by: sort_order}
    
    logger.info(f"Search filter: {filter_dict}")
    logger.info(f"Sort criteria: {sort_dict}")
    
    # Query database
    cursor = db.Listings.find(filter_dict).sort(list(sort_dict.items())).skip(skip).limit(limit)
    
    # Convert to list
    results = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        results.append(ItemResponse(**doc))
    
    logger.info(f"Found {len(results)} results")
    
    return results

@router.get("/categories", response_model=List[str])
async def get_categories(
    db: AsyncIOMotorDatabase = Depends(get_database),
    repo: ItemRepository = Depends(get_item_repository)
):
    """
    Get all available categories
    """
    return await repo.get_categories()

@router.get("/popular-tags", response_model=List[str])
async def get_popular_tags(
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get popular tags
    """
    # Simple implementation - can enhance later
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$project": {"_id": 0, "tag": "$_id"}}
    ]
    
    cursor = db.Listings.aggregate(pipeline)
    tags = []
    async for doc in cursor:
        tags.append(doc["tag"])
    return tags

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
