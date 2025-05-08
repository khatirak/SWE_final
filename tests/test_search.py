import pytest
import os
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
from datetime import datetime, timezone

from backend.main import app
from backend.utilities.models import ItemResponse, ItemCategory

MONGO_URI = os.getenv("MONGO_DETAILS")
TEST_DB_NAME = "nyu_marketplace_test"

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
            "tags": ["outdoor", "sport"],
            "location": "Park",
            "status": "available",
            "created_at": now,
            "seller_id": ""
        },
        {
            "title": "Blue Car",
            "description": "A big blue car",
            "price": 5000,
            "condition": "fair",
            "category": ItemCategory.MISC.value,
            "tags": ["transport"],
            "location": "Garage",
            "status": "available",
            "created_at": now,
            "seller_id": ""
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
        {"title": "A", "description": "", "price": 10, "condition": "good", "category": ItemCategory.BOOKS.value, "tags": ["edible"], "location": "Home", "status": "available", "created_at": now, "seller_id": ""},
        {"title": "B", "description": "", "price": 20, "condition": "good", "category": ItemCategory.BOOKS.value, "tags": ["edible"], "location": "Home", "status": "available", "created_at": now, "seller_id": ""},
        {"title": "C", "description": "", "price": 30, "condition": "good", "category": ItemCategory.BOOKS.value, "tags": ["edible"], "location": "Home", "status": "available", "created_at": now, "seller_id": ""},
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
        {"title": "X", "description": "", "price": 5, "condition": "good", "category": ItemCategory.BOOKS.value, "tags": [], "location": "", "status": "available", "created_at": now, "seller_id": ""},
        {"title": "Y", "description": "", "price": 15, "condition": "good", "category": ItemCategory.ELECTRONICS.value, "tags": [], "location": "", "status": "available", "created_at": now, "seller_id": ""},
        {"title": "Z", "description": "", "price": 25, "condition": "good", "category": ItemCategory.BOOKS.value, "tags": [], "location": "", "status": "available", "created_at": now, "seller_id": ""},
    ]
    await db.Listings.insert_many(docs)
    client.close()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/search/categories")
        assert resp.status_code == 200
        categories = resp.json()
        assert set(categories) == {ItemCategory.BOOKS.value, ItemCategory.ELECTRONICS.value}
