import pytest
from httpx import AsyncClient
from backend.main import app
# import sys
# import asyncio

# if sys.platform == "darwin":
#     asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

async def create_test_listing(ac):
    data = {
        "title": "Test Listing",
        "description": "A good item",
        "price": 100,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["test", "fastapi"],
        "location": "Library",
        "images": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
    }
    response = await ac.post("/listings/", json=data)
    assert response.status_code == 201
    return response.json()["id"]

@pytest.mark.asyncio(loop_scope="session")
async def test_create_listing():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data = {
            "title": "Test Listing",
            "description": "A good item",
            "price": 100,
            "condition": "good",
            "category": "electronics_gadgets",
            "tags": ["test", "fastapi"],
            "location": "Library",
            "images": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
        }
        response = await ac.post("/listings/", json=data)
        assert response.status_code == 201
        assert response.json()["title"] == "Test Listing"

@pytest.mark.asyncio(loop_scope="session")
async def test_get_listing():
    # First create a listing
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # post_resp = await test_create_listing()
        listing_id = await create_test_listing(ac)

        # Now get the listing
        response = await ac.get(f"/listings/{listing_id}")
        assert response.status_code == 200
        assert response.json()["id"] == listing_id

@pytest.mark.asyncio(loop_scope="session")
async def test_update_listing():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        listing_id = await create_test_listing(ac)
        update_data = {
            "title": "Updated Title",
            "price": 150
        }
        response = await ac.put(f"/listings/{listing_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"
        assert response.json()["price"] == 150

@pytest.mark.asyncio(loop_scope="session")
async def test_delete_listing():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        listing_id = await create_test_listing(ac)
        response = await ac.delete(f"/listings/{listing_id}")
        assert response.status_code == 204

        # Confirm it's gone
        response = await ac.get(f"/listings/{listing_id}")
        assert response.status_code == 404

@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_listings():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Simulate a known user
        user_id = "user-123"

        # NOTE: You would ideally mock seller_id or use a fixture to inject it
        # For now, assume that the created listing defaults to seller_id = "100"
        response = await ac.get("/listings/user/100")
        assert response.status_code == 200
        assert isinstance(response.json(), list)