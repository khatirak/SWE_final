import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import status
from backend.main import app

# Use your app's test client

@pytest.mark.asyncio
async def test_redirect_to_search():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/search")
    assert response.status_code == status.HTTP_200_OK  # FastAPI follows redirect by default
    assert response.url.path == "/search/"


@pytest.mark.asyncio
async def test_search_no_params(monkeypatch):
    # Mock the db response with an empty cursor
    class MockCursor:
        async def __aiter__(self):
            return
            yield

    class MockDB:
        class Listings:
            @staticmethod
            def find(*args, **kwargs):
                return MockCursor()

            @staticmethod
            def sort(*args, **kwargs):
                return MockCursor()

            @staticmethod
            def skip(n):
                return MockCursor()

            @staticmethod
            def limit(n):
                return MockCursor()

    monkeypatch.setattr("backend.search.get_database", lambda: MockDB())

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/search/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_categories(monkeypatch):
    mock_categories = ["electronics", "books", "furniture"]

    class MockRepo:
        async def get_categories(self):
            return mock_categories

    monkeypatch.setattr("backend.search.get_item_repository", lambda: MockRepo())

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/search/categories")

    assert response.status_code == 200
    assert response.json() == mock_categories


@pytest.mark.asyncio
async def test_search_with_filters(monkeypatch):
    mock_result = [
        {
            "_id": "507f1f77bcf86cd799439011",
            "title": "Guitar",
            "description": "Nice electric guitar in red",
            "price": 300,
            "category": "electronics",
            "condition": "used",
            "status": "available",
            "created_at": "2023-01-01T00:00:00",
            "seller_id": "507f1f77bcf86cd799439012",
        }
    ]

    class MockCursor:
        def __init__(self, docs):
            self.docs = docs

        def sort(self, *args, **kwargs):
            return self

        def skip(self, n):
            return self

        def limit(self, n):
            return self

        async def __aiter__(self):
            for doc in self.docs:
                yield doc

    class MockDB:
        class Listings:
            @staticmethod
            def find(*args, **kwargs):
                return MockCursor(mock_result)

    monkeypatch.setattr("backend.search.get_database", lambda: MockDB())

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/search/?q=guitar&category=electronics&min_price=100&max_price=500")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["title"] == "Guitar"
    assert data[0]["category"] == "electronics"
