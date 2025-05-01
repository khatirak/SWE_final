import pytest
from httpx import AsyncClient
from backend.main import app

# Optional helper to create dummy listings
async def create_dummy_listing(client: AsyncClient, title: str = "Recent Item"):
    data = {
        "title": title,
        "description": "Testing recent listing endpoint",
        "price": 123,
        "condition": "used",
        "category": "misc_general_items",
        "tags": ["recent"],
        "location": "A5",
        "images": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
    }
    response = await client.post("/listings/", json=data)
    assert response.status_code == 201
    return response.json()

@pytest.mark.asyncio(loop_scope="session")
async def test_get_recent_listings():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 🧪 Create 12 dummy listings to test limit behavior
        for i in range(12):
            await create_dummy_listing(ac, title=f"Recent Item {i}")

        response = await ac.get("/home/recent")
        assert response.status_code == 200

        listings = response.json()
        assert isinstance(listings, list)
        assert len(listings) <= 10  # should return at most 10
        # Ensure they are sorted by created_at (descending)
        created_ats = [item["created_at"] for item in listings]
        assert created_ats == sorted(created_ats, reverse=True)


@pytest.mark.asyncio(loop_scope="session")
async def test_search_listings():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/search/", params={"keyword": "laptop"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

import pytest
from httpx import AsyncClient
from backend.main import app

# 🔧 Create listings for testing
async def create_searchable_listing(client, overrides={}):
    base = {
        "title": "MacBook Pro",
        "description": "Apple laptop in good condition",
        "price": 1200,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["apple", "laptop"],
        "location": "A1",
        "images": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
    }
    base.update(overrides)
    response = await client.post("/listings/", json=base)
    assert response.status_code == 201
    return response.json()

@pytest.mark.asyncio(loop_scope="session")
async def test_search_by_keyword():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await create_searchable_listing(ac, {"title": "Super fast laptop"})
        await create_searchable_listing(ac, {"title": "Old chair"})

        response = await ac.get("/search/", params={"keyword": "laptop"})
        assert response.status_code == 200
        data = response.json()
        assert all("laptop" in item["title"].lower() or "laptop" in item["description"].lower() for item in data)

@pytest.mark.asyncio(loop_scope="session")
async def test_search_by_category():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await create_searchable_listing(ac, {"category": "books_stationery"})
        await create_searchable_listing(ac, {"category": "furniture"})

        response = await ac.get("/search/", params={"category": "books_stationery"})
        assert response.status_code == 200
        data = response.json()
        assert all(item["category"] == "books_stationery" for item in data)

@pytest.mark.asyncio(loop_scope="session")
async def test_search_by_price_range():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await create_searchable_listing(ac, {"price": 300})
        await create_searchable_listing(ac, {"price": 1000})

        response = await ac.get("/search/", params={"min_price": 200, "max_price": 500})
        assert response.status_code == 200
        data = response.json()
        assert all(200 <= item["price"] <= 500 for item in data)

@pytest.mark.asyncio(loop_scope="session")
async def test_search_by_condition():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await create_searchable_listing(ac, {"condition": "brand_new"})
        await create_searchable_listing(ac, {"condition": "used"})

        response = await ac.get("/search/", params={"condition": "brand_new"})
        assert response.status_code == 200
        data = response.json()
        assert all(item["condition"] == "brand_new" for item in data)

@pytest.mark.asyncio(loop_scope="session")
async def test_search_by_tag():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await create_searchable_listing(ac, {"tags": ["tech", "macbook"]})
        await create_searchable_listing(ac, {"tags": ["furniture", "chair"]})

        response = await ac.get("/search/", params={"tags": ["tech"]})
        assert response.status_code == 200
        data = response.json()
        assert any("tech" in item["tags"] for item in data)

@pytest.mark.asyncio(loop_scope="session")
async def test_search_sort_by_price():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await create_searchable_listing(ac, {"price": 100})
        await create_searchable_listing(ac, {"price": 800})
        await create_searchable_listing(ac, {"price": 300})

        response = await ac.get("/search/", params={"sort_by": "price", "sort_order": "asc"})
        assert response.status_code == 200
        prices = [item["price"] for item in response.json()]
        assert prices == sorted(prices)