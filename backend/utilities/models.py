from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ItemCondition(str, Enum):
    """Enum for possible item conditions as specified in requirements [R-104]"""
    BRAND_NEW = "brand_new"
    OPENED_UNUSED = "opened_unused"
    GOOD = "good"
    USED = "used"

class ItemCategory(str, Enum):
    """Enum for item categories as specified in requirements [R-105]"""
    APPAREL = "apparel_accessories"
    FURNITURE = "furniture"
    HOME_APPLIANCES = "home_appliances"
    BOOKS = "books_stationery"
    BEAUTY = "beauty_personal_care"
    ELECTRONICS = "electronics_gadgets"
    MISC = "misc_general_items"

class ListingStatus(str, Enum):
    """Enum for listing status as specified in requirements [R-304]"""
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"

class ImageModel(BaseModel):
    """Model for item images"""
    url: str
    thumbnail_url: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://storage.example.com/images/item123.jpg",
                "thumbnail_url": "https://storage.example.com/thumbnails/item123.jpg"
            }
        }

class ItemBase(BaseModel):
    """Base model for marketplace items"""
    title: str = Field(..., min_length=1, max_length=100, description="Item title, max 100 characters [R-101]")
    description: str = Field(..., min_length=10, max_length=1000, description="Item description, max 200 words [R-102]")
    price: float = Field(..., ge=0, description="Item price, must be zero or positive [R-103]")
    condition: ItemCondition = Field(..., description="Item condition [R-104]")
    category: ItemCategory = Field(..., description="Item category [R-105]")
    tags: List[str] = Field(default=[], description="Optional tags for better searchability")
    location: Optional[str] = Field(None, description="Campus location for item pickup")

class ItemCreate(ItemBase):
    """Model for creating a new item listing"""
    images: List[str] = Field(..., min_items=2, max_items=10, description="Image URLs, 2-10 required [R-106]")

class ItemUpdate(BaseModel):
    """Model for updating an existing item"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    price: Optional[float] = Field(None, ge=0)
    condition: Optional[ItemCondition] = None
    category: Optional[ItemCategory] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None
    images: Optional[List[str]] = None
    status: Optional[ListingStatus] = None

class ItemResponse(ItemBase):
    """Model for item response"""
    id: str
    seller_id: str
    images: List[ImageModel]
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: ListingStatus = ListingStatus.AVAILABLE
    reservation_count: Optional[int] = 0
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60d21b4967d0d8992e610c85",
                "title": "MacBook Pro 2021",
                "description": "16-inch, M1 chip, excellent condition",
                "price": 4500,
                "condition": "good",
                "category": "electronics_gadgets",
                "tags": ["laptop", "apple", "macbook"],
                "location": "D2 Building",
                "seller_id": "60d21b4967d0d8992e610c85",
                "images": [{"url": "https://example.com/image1.jpg"}],
                "created_at": "2025-03-15T12:00:00Z",
                "updated_at": "2025-03-15T12:00:00Z",
                "status": "available",
                "reservation_count": 0
            }
        }

class UserBase(BaseModel):
    """Base model for users"""
    email: EmailStr = Field(..., description="NYU email address")
    name: str = Field(..., description="User's full name")
    
    @validator('email')
    def email_must_be_nyu(cls, v):
        """Validate that email is from NYU domain"""
        if not v.endswith('@nyu.edu'):
            raise ValueError('Email must be from NYU domain (@nyu.edu)')
        return v

class UserCreate(UserBase):
    """Model for creating a new user"""
    pass

class UserResponse(UserBase):
    """Model for user response"""
    id: str
    created_at: datetime
    listings: List[str] = []
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60d21b4967d0d8992e610c85",
                "email": "abc123@nyu.edu",
                "name": "John Doe",
                "created_at": "2025-03-15T12:00:00Z",
                "listings": ["60d21b4967d0d8992e610c85"]
            }
        }

class ReservationBase(BaseModel):
    """Base model for reservation requests"""
    listing_id: str
    buyer_id: str

class ReservationCreate(ReservationBase):
    """Model for creating a new reservation request"""
    pass

class ReservationResponse(ReservationBase):
    """Model for reservation response"""
    id: str
    created_at: datetime
    status: str = "pending"  # pending, confirmed, declined, expired
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60d21b4967d0d8992e610c85",
                "listing_id": "60d21b4967d0d8992e610c85",
                "buyer_id": "60d21b4967d0d8992e610c85",
                "created_at": "2025-03-15T12:00:00Z",
                "status": "pending"
            }
        }

class SearchFilters(BaseModel):
    """Model for search filters"""
    keyword: Optional[str] = None
    category: Optional[ItemCategory] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    condition: Optional[ItemCondition] = None
    status: Optional[ListingStatus] = ListingStatus.AVAILABLE
    tags: Optional[List[str]] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"
    
    class Config:
        schema_extra = {
            "example": {
                "keyword": "macbook",
                "category": "electronics_gadgets",
                "min_price": 1000,
                "max_price": 5000,
                "condition": "good",
                "status": "available",
                "tags": ["laptop"],
                "sort_by": "price",
                "sort_order": "asc"
            }
        }
