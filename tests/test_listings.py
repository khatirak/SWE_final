# tests/test_listings.py

import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
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

@pytest.mark.asyncio
async def test_search_listings():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/search", params={"keyword": "laptop"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)