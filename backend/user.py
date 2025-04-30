from fastapi import APIRouter, Request, HTTPException, status, Depends
from backend.app.user import router as user_router
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.db.repository import UserRepository
from backend.db.database import get_database

# Model for phone update
class PhoneUpdate(BaseModel):
    phoneNumber: str

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# Add the update-phone endpoint directly here
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

# Re-export all routes from user_router
router.include_router(user_router, prefix="") 