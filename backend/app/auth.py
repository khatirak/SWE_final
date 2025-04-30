from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
import logging

from utilities.models import UserCreate, UserResponse
from db.repository import UserRepository
from db.database import get_database
from utilities.helpers import validate_nyu_email

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
config = Config('.env')
oauth = OAuth(config)

# Google OAuth setup
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account',  # Always show account selector
    },
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

@router.get("/login")
async def login(request: Request):
    """
    Redirect to Google OAuth login [R-001]
    
    This endpoint initiates the OAuth flow with Google,
    redirecting the user to Google's authentication page.
    
    Args:
        request: HTTP request
        
    Returns:
        Redirect to Google authentication
    """
    try:
        # Generate the callback URL
        redirect_uri = request.url_for('auth_callback')
        logger.info(f"Generated redirect URI: {redirect_uri}")
        
        # Get the authorization URL
        auth_url = await oauth.google.authorize_redirect(request, redirect_uri)
        logger.info(f"Authorization URL: {auth_url.headers.get('location')}")
        
        return auth_url
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate login: {str(e)}"
        )

@router.get("/callback")
async def auth_callback(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Handle OAuth callback from Google [R-001]
    
    This endpoint handles the callback from Google OAuth,
    verifies the email domain is @nyu.edu, and creates/retrieves the user.
    
    Args:
        request: HTTP request with OAuth data
        db: Database connection
        
    Returns:
        Redirect to frontend home page
    """
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info.get('email_verified') or not user_info.get('email'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not verified by Google"
            )
            
        email = user_info['email']
        if not email.endswith('@nyu.edu'):
            logger.warning(f"Rejected non-NYU email: {email}")
            return RedirectResponse(url="http://localhost:3000/?error=invalid_email")
            
        # Get or create user
        user_repo = UserRepository(db)
        user = await user_repo.get_user_by_email(email)
        
        if not user:
            # Create new user
            new_user = UserCreate(
                email=email,
                name=user_info.get('name', '')
            )
            user = await user_repo.create_user(new_user)
        
        # Store user in session
        request.session['user'] = {
            'id': user.id,
            'email': user.email,
            'name': user.name
        }
        
        # Redirect to frontend home page
        frontend_url = "http://localhost:3000"
        return RedirectResponse(url=frontend_url)
    
    except OAuthError as e:
        logger.error(f"OAuth error: {str(e)}")
        return RedirectResponse(url="http://localhost:3000/?error=oauth_error")
    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        return RedirectResponse(url="http://localhost:3000/?error=authentication_failed")

    # except OAuthError as e:
    #     logger.error(f"OAuth error: {str(e)}")
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=str(e)
    #     )
    # except Exception as e:
    #     logger.error(f"Callback error: {str(e)}")
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"Authentication failed: {str(e)}"
    #     )

@router.get("/logout")
async def logout(request: Request):
    """
    Log out user by clearing session and redirecting to frontend
    
    Args:
        request: HTTP request
        
    Returns:
        Redirect to frontend home page
    """
    try:
        # Clear the session
        request.session.clear()
        
        # Redirect to frontend home page
        frontend_url = "http://localhost:3000"
        return RedirectResponse(url=frontend_url)
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get current authenticated user
    
    Args:
        request: HTTP request
        db: Database connection
        
    Returns:
        Current user data
    """
    user = request.session.get('user')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user_repo = UserRepository(db)
    return await user_repo.get_user_by_id(user['id'])