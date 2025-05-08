import os
import pytest
from datetime import datetime, timedelta,timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient

from backend.db.repository import ItemRepository
from backend.utilities.models import ItemResponse,ItemCategory
from backend.main import app


MONGO_URI = os.getenv("MONGO_DETAILS")
TEST_DB_NAME = "nyu_marketplace_test"
TEST_USER_ID = "6812ab34fc012c5355f44c0e"

@pytest.mark.asyncio
async def test_get_recent_default_limit_and_order():
    # connect to the same test DB as test_db_setup
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[TEST_DB_NAME]
    now = datetime.now(timezone.utc)

    docs = []
    for i in range(5):
        doc = {
            "_id": ObjectId(),
            "title": "test",
            "description": "testtest",
            "seller_id": ObjectId(),
            "price": i,
            "status": "available",
            "created_at": now - timedelta(minutes=i),
            "category": ItemCategory.APPAREL,
            # alternate None and an ObjectId for buyerId
            "buyerId": None if i % 2 == 0 else ObjectId()
        }
        docs.append(doc)
    await db.Listings.insert_many(docs)
    client.close()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # call without specifying limit or category
        resp = await ac.get("/home/recent")
        assert resp.status_code == 200
        recent = [ItemResponse(**d) for d in resp.json()]
        assert len(recent) == 5
        # expect them in descending created_at order
        expected_order = sorted(docs, key=lambda d: d["created_at"], reverse=True)
        assert [item.id for item in recent] == [str(d["_id"]) for d in expected_order]

        # test that buyerId was stringified when present and stays None otherwise
        for original, returned in zip(expected_order, recent):
            if original["buyerId"] is None:
                assert returned.buyerId is None
            else:
                assert returned.buyerId == str(original["buyerId"])

        # test a smaller limit
        resp = await ac.get("/home/recent", params={"limit":3})
        assert resp.status_code == 200
        recent3 = [ItemResponse(**d) for d in resp.json()]
        assert len(recent3) == 3
        assert [r.id for r in recent3] == [str(d["_id"]) for d in expected_order[:3]]

        client.close()
@pytest.mark.asyncio
async def test_get_recent_with_category_filter_endpoint():
    # 1) Prepare test data in DB
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[TEST_DB_NAME]
    await db.Listings.delete_many({})

    now = datetime.now(timezone.utc)
    electronics_doc = {
        "_id": ObjectId(),
        "title": "Electronic Thing",
        "description": "Shiny and new",
        "seller_id": ObjectId(),
        "price": 50,
        "status": "available",
        "created_at": now,
        "category": ItemCategory.ELECTRONICS,  # insert the enum itself
        "tags": [],
        "location": "Anywhere",
        "images": [],
    }
    apparel_doc = {
        "_id": ObjectId(),
        "title": "T-Shirt",
        "description": "Cotton tee",
        "seller_id": ObjectId(),
        "price": 20,
        "status": "available",
        "created_at": now - timedelta(minutes=1),
        "category": ItemCategory.APPAREL,
        "tags": [],
        "location": "Anywhere",
        "images": [],
    }
    await db.Listings.insert_many([electronics_doc, apparel_doc])
    client.close()

    # 2) Call the /home/recent endpoint with a category filter
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Filter for ELECTRONICS
        resp = await ac.get(
            "/home/recent",
            params={"category": ItemCategory.ELECTRONICS.value}
        )
        assert resp.status_code == 200
        data = resp.json()
        # Only the electronics listing should come back
        assert len(data) == 1
        item = ItemResponse(**data[0])
        assert item.id == str(electronics_doc["_id"])
        assert item.category == ItemCategory.ELECTRONICS

        # Now filter for APPAREL
        resp2 = await ac.get(
            "/home/recent",
            params={"category": ItemCategory.APPAREL.value}
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert len(data2) == 1
        item2 = ItemResponse(**data2[0])
        assert item2.id == str(apparel_doc["_id"])
        assert item2.category == ItemCategory.APPAREL