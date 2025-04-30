# backend/db/database.py
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

ca = certifi.where()

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGO_DETAILS")
DATABASE_NAME = os.getenv("DATABASE_NAME", "Bazaar")


# Create MongoDB client
client = AsyncIOMotorClient(MONGODB_URL, tlsCAFile=ca)
db = client[DATABASE_NAME]

async def get_database() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """
    Dependency for getting MongoDB database instance.
    """
    try:
        yield db
    finally:
        pass  # Connection is managed by the client 