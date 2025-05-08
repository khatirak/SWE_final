import os
import asyncio
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from types import AsyncGeneratorType
from httpx import AsyncClient
import datetime

from backend.main import app
from backend.db import database
from backend.app.auth import get_current_user
from backend.utilities.models import UserResponse


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

