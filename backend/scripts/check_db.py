import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_database():
    # Get MongoDB connection string from environment
    MONGODB_URL = os.getenv("MONGO_DETAILS")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "Bazaar")
    
    print(f"Connecting to database: {DATABASE_NAME}")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Check listings collection
    print("\nChecking Listings collection:")
    cursor = db.Listings.find({})
    listings = []
    async for doc in cursor:
        listings.append(doc)
    
    print(f"Found {len(listings)} listings")
    
    if listings:
        print("\nSample of listings:")
        for listing in listings[:3]:  # Show first 3 listings
            print(f"\nTitle: {listing.get('title')}")
            print(f"Description: {listing.get('description')}")
            print(f"Status: {listing.get('status')}")
            print(f"Category: {listing.get('category')}")
            print("-" * 50)
    
    # Check distinct categories
    categories = await db.Listings.distinct("category")
    print(f"\nAvailable categories: {categories}")
    
    # Check distinct statuses
    statuses = await db.Listings.distinct("status")
    print(f"\nAvailable statuses: {statuses}")

if __name__ == "__main__":
    asyncio.run(check_database()) 