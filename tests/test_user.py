import pytest
from bson import ObjectId
from httpx import AsyncClient
from backend.main import app
import os

# Constants
TEST_USER_ID = "6812ab34fc012c5355f44c0e"
OTHER_USER_ID = "64f1c9a2e4b0c23b9f5e0a2c"
NON_EXISTENT_ID = "64f1c9a2e4b0c23b9f5e0a1b"


@pytest.mark.asyncio
async def test_get_user_by_id_success(ac: AsyncClient, event_loop):
    # 1) seed the test user into the users collection
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    client = AsyncIOMotorClient(os.getenv("MONGO_DETAILS"))
    db = client["nyu_marketplace_test"]
    await db.users.insert_one({
        "_id": ObjectId(TEST_USER_ID),
        "email": "foo@example.com",
        "name": "Foo Bar",
        "phone": "1234567890"
    })

    # 2) exercise the endpoint
    response = await ac.get(f"/user/{TEST_USER_ID}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == TEST_USER_ID
    assert data["email"] == "foo@example.com"
    assert data["name"] == "Foo Bar"
    assert data["phone"] == "1234567890"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(ac: AsyncClient):
    response = await ac.get(f"/user/{NON_EXISTENT_ID}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_my_listings(ac: AsyncClient):

     # sure that DB is empty?
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.getenv("MONGO_DETAILS"))
    db = client["nyu_marketplace_test"]
    count = await db.Listings.count_documents({})
    assert count == 0, f"Expected empty test DB, found {count} listings"

    # create two listings as TEST_USER_ID
    print("Overrides:", app.dependency_overrides.keys())

    payload = {
        "title": "List Test",
        "description": "Testing get_my_listings",
        "price": 60,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["list"],
        "location": "TestLoc",
        "seller_id": TEST_USER_ID,
        "images": ["https://example.com/1.jpg", "https://example.com/2.jpg"]
    }
    r1 = await ac.post("/listings/", json=payload)
    r2 = await ac.post("/listings/", json=payload)
    assert r1.status_code == 201 and r2.status_code == 201

    # fetch listings for the test user
    response = await ac.get(f"/user/{TEST_USER_ID}/listings")
    assert response.status_code == 200
    items = response.json()
    assert all(item["seller_id"] == TEST_USER_ID for item in items)
    assert len(items) == 2


@pytest.mark.asyncio
async def test_get_my_listings_empty(ac: AsyncClient):
    response = await ac.get(f"/user/{OTHER_USER_ID}/listings")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_my_requests(ac: AsyncClient):
    # create a listing and request
    payload = {
        "title": "Request Test",
        "description": "Testing get_my_requests",
        "price": 80,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["req"],
        "location": "TestLoc",
        "images": ["https://example.com/a.jpg", "https://example.com/b.jpg"]
    }
    create = await ac.post("/listings/", json=payload)
    item_id = create.json()["id"]
    await ac.post(f"/listings/{item_id}/request/{TEST_USER_ID}")
    await ac.post(f"/listings/{item_id}/confirm")
    # fetch requests for that user
    response = await ac.get(f"/user/{TEST_USER_ID}/my_requests")
    assert response.status_code == 200
    reqs = response.json()
    assert any(r["listing_id"] == item_id for r in reqs)


@pytest.mark.asyncio
async def test_get_my_requests_empty(ac: AsyncClient):
    response = await ac.get(f"/user/{OTHER_USER_ID}/my_requests")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_my_request_for_item(ac: AsyncClient):
    # create one listing and one request
    payload = {
        "title": "Single Request Test",
        "description": "Testing get_my_requests/{item_id}",
        "price": 90,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["single"],
        "location": "TestLoc",
        "images": ["https://example.com/x.jpg", "https://example.com/y.jpg"]
    }
    create = await ac.post("/listings/", json=payload)
    item_id = create.json()["id"]
    await ac.post(f"/listings/{item_id}/request/{TEST_USER_ID}")

    # fetch for that specific item
    response = await ac.get(f"/user/{TEST_USER_ID}/my_requests/{item_id}")
    assert response.status_code == 200
    reqs = response.json()
    assert len(reqs) == 1
    assert reqs[0]["listing_id"] == item_id


@pytest.mark.asyncio
async def test_update_phone_unauthenticated(ac: AsyncClient):
    # no session => HTTP 401
    resp = await ac.post("/user/update-phone", json={"phoneNumber": "9999999999"})
    assert resp.status_code == 401