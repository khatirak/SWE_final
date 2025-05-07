import pytest
from httpx import AsyncClient

# Assuming standard user ID used in override_get_current_user
TEST_USER_ID = "6812ab34fc012c5355f44c0e"

@pytest.mark.asyncio
async def test_update_listing_status(ac: AsyncClient):
    response = await ac.post("/listings/", json={
        "title": "Test Item",
        "description": "For status update test",
        "price": 200,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["update"],
        "location": "Campus",
        "images": ["https://example.com/img.jpg", "https://example.com/img.jpg"]
    })
    item_id = response.json()["id"]

    # Update the status to "reserved"
    response = await ac.put(f"/listings/{item_id}/status", params={"status": "reserved"})
    assert response.status_code == 200
    assert response.json()["status"] == "reserved"

@pytest.mark.asyncio
async def test_request_and_confirm_reservation(ac: AsyncClient):
    # Create listing
    response = await ac.post("/listings/", json={
        "title": "Reservation Test",
        "description": "Testing reservation",
        "price": 150,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["reservation"],
        "location": "Library",
        "images": ["https://example.com/img.jpg", "https://example.com/img.jpg"]
    })
    item_id = response.json()["id"]

    # Request reservation
    response = await ac.post(f"/listings/{item_id}/request/{TEST_USER_ID}")
    assert response.status_code == 200

    # Confirm reservation
    response = await ac.post(f"/listings/{item_id}/confirm", json={"buyer_id": TEST_USER_ID})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_reservations(ac: AsyncClient):
    # Create listing
    response = await ac.post("/listings/", json={
        "title": "Get Reservations Test",
        "description": "Test reservations",
        "price": 120,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["get"],
        "location": "Dorm",
        "images": ["https://example.com/img.jpg", "https://example.com/img.jpg"]
    })
    item_id = response.json()["id"]

    # Request reservation
    await ac.post(f"/listings/{item_id}/request/{TEST_USER_ID}")

    # Fetch reservations
    response = await ac.get(f"/listings/{item_id}/reservations")
    assert response.status_code == 200
    assert any(r["buyer_id"] == TEST_USER_ID for r in response.json())

@pytest.mark.asyncio
async def test_cancel_reservation(ac: AsyncClient):
    # Create listing
    response = await ac.post("/listings/", json={
        "title": "Cancel Reservation Test",
        "description": "Test cancel",
        "price": 180,
        "status": "available",
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["cancel"],
        "location": "Gym",
        "images": ["https://example.com/img.jpg", "https://example.com/img.jpg"]
    })
    item_id = response.json()["id"]

    # Request reservation
    await ac.post(f"/listings/{item_id}/request/{TEST_USER_ID}")

    # Cancel reservation
    response = await ac.delete(f"/listings/{item_id}/cancel_reservation", params={"buyer_id": TEST_USER_ID})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_mark_listing_as_sold(ac: AsyncClient):
    # Create listing
    response = await ac.post("/listings/", json={
        "title": "Sold Test",
        "description": "Mark as sold",
        "price": 100,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["sold"],
        "location": "Lab",
        "images": ["https://example.com/img.jpg", "https://example.com/img.jpg"]
    })
    item_id = response.json()["id"]

    # Mark as sold
    response = await ac.post(f"/listings/{item_id}/sold")
    assert response.status_code == 200
    assert "marked as sold" in response.json()["message"].lower()