import pytest
import os
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
from datetime import datetime, timezone

from backend.main import app
from backend.utilities.models import ItemResponse, ItemCategory, ListingStatus

MONGO_URI = os.getenv("MONGO_DETAILS")
TEST_DB_NAME = "nyu_marketplace_test"
TEST_USER_ID = "6812ab34fc012c5355f44c0e"

@pytest.mark.asyncio
async def test_redirect_to_search():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/search")
        assert response.status_code in (301, 302, 307, 308)
        assert response.headers["location"] == "/search/"

@pytest.mark.asyncio
async def test_search_listings_full_text():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[TEST_DB_NAME]
    now = datetime.now(timezone.utc).isoformat()
    docs = [
        {
            "title": "Red Bicycle",
            "description": "A fast red bike",
            "price": 150,
            "condition": "good",
            "category": ItemCategory.ELECTRONICS.value,
            "location": "Park",
            "status": "available",
            "created_at": now,
            "seller_id": TEST_USER_ID
        },
        {
            "title": "Blue Car",
            "description": "A big blue car",
            "price": 5000,
            "condition": "fair",
            "category": ItemCategory.MISC.value,
            "location": "Garage",
            "status": "available",
            "created_at": now,
            "seller_id": TEST_USER_ID
        }
    ]
    await db.Listings.insert_many(docs)
    client.close()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/search/", params={"q": "red"})
        assert resp.status_code == 200
        items = [ItemResponse(**d) for d in resp.json()]
        assert len(items) == 1
        assert items[0].title == "Red Bicycle"

@pytest.mark.asyncio
async def test_search_listings_filters_and_sort():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[TEST_DB_NAME]
    now = datetime.now(timezone.utc).isoformat()
    docs = [
        {"title": "A", "description": "", "price": 10, "condition": "good", "category": ItemCategory.BOOKS.value, "status": "available", "created_at": now, "seller_id": TEST_USER_ID},
        {"title": "B", "description": "", "price": 20, "condition": "good", "category": ItemCategory.BOOKS.value, "status": "available", "created_at": now, "seller_id": TEST_USER_ID},
        {"title": "C", "description": "", "price": 30, "condition": "good", "category": ItemCategory.BOOKS.value, "status": "available", "created_at": now, "seller_id": TEST_USER_ID},
    ]
    await db.Listings.insert_many(docs)
    client.close()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/search/", params={
            "min_price": 15,
            "sort_by": "price",
            "sort_order": 1
        })
        assert resp.status_code == 200
        items = [ItemResponse(**d) for d in resp.json()]
        prices = [item.price for item in items]
        assert prices == [20, 30]

@pytest.mark.asyncio
async def test_get_categories():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[TEST_DB_NAME]
    now = datetime.now(timezone.utc).isoformat()
    docs = [
        {"title": "X", "description": "", "price": 5, "condition": "good", "category": ItemCategory.BOOKS.value, "location": "", "status": "available", "created_at": now, "seller_id": TEST_USER_ID},
        {"title": "Y", "description": "", "price": 15, "condition": "good", "category": ItemCategory.ELECTRONICS.value, "location": "", "status": "available", "created_at": now, "seller_id": TEST_USER_ID},
        {"title": "Z", "description": "", "price": 25, "condition": "good", "category": ItemCategory.BOOKS.value, "location": "", "status": "available", "created_at": now, "seller_id": TEST_USER_ID},
    ]
    await db.Listings.insert_many(docs)
    client.close()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/search/categories")
        assert resp.status_code == 200
        categories = resp.json()
        assert set(categories) == {ItemCategory.BOOKS.value, ItemCategory.ELECTRONICS.value}

@pytest.mark.asyncio
async def test_search_by_category():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[TEST_DB_NAME]
    now = datetime.now(timezone.utc).isoformat()
    docs = [
        {"title": "Book1", "description": "Good read", "price": 10, "condition": "good", "category": ItemCategory.BOOKS.value, "status": "available", "created_at": now, "seller_id": TEST_USER_ID},
        {"title": "Chair", "description": "Wooden chair", "price": 20, "condition": "good", "category": ItemCategory.FURNITURE.value,  "status": "available", "created_at": now, "seller_id": TEST_USER_ID},
    ]
    await db.Listings.insert_many(docs)
    client.close()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/search/", params={"category": ItemCategory.BOOKS.value})
        assert resp.status_code == 200
        items = [ItemResponse(**d) for d in resp.json()]
        assert all(item.category == ItemCategory.BOOKS.value for item in items)
        assert len(items) == 1

@pytest.mark.asyncio
async def test_search_by_price_filters():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[TEST_DB_NAME]
    now = datetime.now(timezone.utc).isoformat()
    docs = [
        {"title": "Cheap", "description": "Low price", "price": 5, "condition": "good", "category": ItemCategory.MISC.value,  "status": "available", "created_at": now, "seller_id": TEST_USER_ID},
        {"title": "Mid", "description": "Medium price", "price": 15, "condition": "good", "category": ItemCategory.MISC.value,  "status": "available", "created_at": now, "seller_id": TEST_USER_ID},
        {"title": "Expensive", "description": "High price", "price": 25, "condition": "good", "category": ItemCategory.MISC.value,  "status": "available", "created_at": now, "seller_id": TEST_USER_ID},
    ]
    await db.Listings.insert_many(docs)
    client.close()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # max_price filter
        resp = await ac.get("/search/", params={"max_price": 10})
        items = [ItemResponse(**d) for d in resp.json()]
        assert [item.price for item in items] == [5]

        # min_price filter
        resp = await ac.get("/search/", params={"min_price": 20})
        items = [ItemResponse(**d) for d in resp.json()]
        assert [item.price for item in items] == [25]

@pytest.mark.asyncio
async def test_search_by_status_and_buyer():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[TEST_DB_NAME]
    now = datetime.now(timezone.utc).isoformat()
    buyer = "buyer123"
    docs = [
        {"title": "ReservedItem", "description": "Reserved list", "price": 100, "condition": "good", "category": ItemCategory.MISC.value,  "status": ListingStatus.RESERVED.value, "buyerId": buyer, "created_at": now, "seller_id": TEST_USER_ID},
        {"title": "AvailableItem", "description": "Available list", "price": 50, "condition": "good", "category": ItemCategory.MISC.value, "status": ListingStatus.AVAILABLE.value, "created_at": now, "seller_id": TEST_USER_ID},
    ]
    await db.Listings.insert_many(docs)
    client.close()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/search/", params={"status": ListingStatus.RESERVED.value})
        assert resp.status_code == 200
        items = [ItemResponse(**d) for d in resp.json()]
        assert len(items) == 1
        item = items[0]
        assert item.status == ListingStatus.RESERVED.value
        assert item.buyerId == "buyer123"

