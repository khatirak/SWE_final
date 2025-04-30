from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.auth import router as auth_router
from app.listing import router as listing_router
from app.search import router as search_router
from app.home import router as home_router

app = FastAPI()

# Mount static files directory
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(listing_router)
app.include_router(search_router)
app.include_router(home_router)

@app.get("/")
async def root():
    return {"message": "Welcome to NYU Marketplace API"} 