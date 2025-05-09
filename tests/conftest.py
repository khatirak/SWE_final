
import os
import asyncio
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from types import AsyncGeneratorType
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
import os
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from backend.main import app

@pytest.fixture(scope="session", autouse=True)
def test_db_setup(event_loop):
    # 1) Connect to the test database
    mongo_uri = os.getenv("MONGO_DETAILS")
    client = AsyncIOMotorClient(mongo_uri)
    test_db = client["nyu_marketplace_test"]

    # 2) Override get_database -> nyu_marketplace_test
    import backend.db.database
    async def override_get_database():
        print("override_get_database was used")
        yield test_db

    app.dependency_overrides[
        backend.db.database.get_database
    ] = override_get_database

    yield  # run your tests…

    # 3) Teardown: drop the test DB on the same loop you’ve been using
    event_loop.run_until_complete(
        client.drop_database("nyu_marketplace_test")
    )
    client.close()

    # 4) Only remove the one override we added
    app.dependency_overrides.pop(
        backend.db.database.get_database,
        None
    )

# ─── 3) Ensure each test starts with a clean listings collection ─────────────

@pytest_asyncio.fixture(autouse=True)
async def clear_listings_db():
    client = AsyncIOMotorClient(os.getenv("MONGO_DETAILS"))
    db = client["nyu_marketplace_test"]

    # clear before
    await db.Listings.delete_many({})

    yield

    # clear after
    await db.Listings.delete_many({})
    
    client.close()

# ─── 4) Override authentication for all tests) Override authentication for all tests ────────────────────────────────
@pytest.fixture(autouse=True)
def override_get_current_user():
    app.dependency_overrides[get_current_user] = lambda: UserResponse(
        id="6812ab34fc012c5355f44c0e",
        email="test@example.com",
        name="Test User",
    )
    yield
    app.dependency_overrides.pop(get_current_user, None)

# ─── 5) AsyncClient fixture for tests ───────────────────────────────────────
@pytest_asyncio.fixture
async def ac():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client