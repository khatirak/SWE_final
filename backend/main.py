from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.sessions import SessionMiddleware
import os

from app.auth import router as auth_router
from app.home import router as home_router
from app.listing import router as listing_router
from app.search import router as search_router
from db.database import client

app = FastAPI(
    title="NYU Marketplace API",
    description="API for the NYU Marketplace platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),  # Will raise error if not set
)

# Include routers
app.include_router(auth_router)
app.include_router(home_router)
app.include_router(listing_router)
app.include_router(search_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
