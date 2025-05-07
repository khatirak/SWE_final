import os
import asyncio
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient

from backend.main import app
from backend.db import database
from backend.app.auth import get_current_user
from backend.utilities.models import UserResponse

# ─── 1) Persistent event loop for all async tests ─────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# ─── 2) Redirect DB calls to a dedicated test database ────────────────────────
@pytest.fixture(scope="session", autouse=True)
def test_db_setup():
    """
    Override database.get_database to point at a test database,
    and drop it when the session ends without requiring an active event loop.
    """
    mongo_uri = os.getenv("MONGO_DETAILS")
    if not mongo_uri:
        raise RuntimeError("MONGO_DETAILS env var must be set for tests")
    client = AsyncIOMotorClient(mongo_uri)
    test_db = client["nyu_marketplace_test"]
    # Monkey-patch get_database directly
    database.get_database = lambda: test_db
    yield
    # Drop the test database via the underlying pymongo client to avoid async loop
    client.delegate.drop_database("nyu_marketplace_test")

# ─── 3) Ensure each test starts with a clean listings collection ─────────────
@pytest_asyncio.fixture(autouse=True)
async def clear_listings_db():
    db = database.get_database()
    await db.listings.delete_many({})
    yield
    await db.listings.delete_many({})

# ─── 4) Override authentication for all tests ────────────────────────────────
@pytest.fixture(autouse=True)
def override_get_current_user():
    app.dependency_overrides[get_current_user] = lambda: UserResponse(
        id="681305df4a7bf9e51b6e805e",
        email="test@example.com",
        name="Test User",
    )
    yield
    app.dependency_overrides.clear()

# ─── 5) AsyncClient fixture for tests ───────────────────────────────────────
@pytest_asyncio.fixture
async def ac():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# ─── 6) Helper: create a listing ────────────────────────────────────────────
async def create_test_listing(ac: AsyncClient) -> str:
    payload = {
        "title":       "Test Listing",
        "description": "A good item",
        "price":       100,
        "condition":   "good",
        "category":    "electronics_gadgets",
        "tags":        ["test", "fastapi"],
        "location":    "Library",
        "images":      [
            "https://example.com/img1.jpg",
            "https://example.com/img2.jpg",
        ],
    }
    resp = await ac.post("/listings/", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]

# ─── 7) CRUD tests ───────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_create_listing(ac):
    listing_id = await create_test_listing(ac)
    r = await ac.get(f"/listings/{listing_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Test Listing"

@pytest.mark.asyncio
async def test_get_listing(ac):
    listing_id = await create_test_listing(ac)
    r = await ac.get(f"/listings/{listing_id}")
    assert r.status_code == 200
    assert r.json()["id"] == listing_id

@pytest.mark.asyncio
async def test_update_listing(ac):
    listing_id = await create_test_listing(ac)
    update = {"title": "Updated Title", "price": 150}
    r = await ac.put(f"/listings/{listing_id}", json=update)
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Updated Title"
    assert body["price"] == 150

@pytest.mark.asyncio
async def test_delete_listing(ac):
    listing_id = await create_test_listing(ac)
    r = await ac.delete(f"/listings/{listing_id}")
    assert r.status_code == 204
    # Confirm deletion
    r2 = await ac.get(f"/listings/{listing_id}")
    assert r2.status_code == 404