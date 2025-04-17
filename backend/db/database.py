from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
from typing import AsyncGenerator
import os

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "nyu_marketplace")

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