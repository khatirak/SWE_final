from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = 'Bazaar'

# Print debug info to help diagnose
print(f"MONGODB_URL from env: {MONGODB_URL}")
print(f"Using DATABASE_NAME: {DATABASE_NAME}")

# Create MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

async def get_database() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """
    Dependency for getting MongoDB database instance.
    """
    try:
        yield db
    finally:
        pass  # Connection is managed by the client 