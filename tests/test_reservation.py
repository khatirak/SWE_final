import pytest
from httpx import AsyncClient
from bson import ObjectId

# Assuming standard user ID used in override_get_current_user
TEST_USER_ID = "6812ab34fc012c5355f44c0e"
OTHER_USER_ID = "56adfdb34fc012c5355f44c0"


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


@pytest.mark.asyncio
async def test_get_reservations_reserved_branch(ac):
    # 1) Create a fresh listing
    resp = await ac.post("/listings/", json={
        "title": "Reserved Branch Test",
        "description": "Ensure only the confirmed reservation is returned",
        "price": 100,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["reserved"],
        "location": "Dorm",
        "images": ["https://example.com/img1.jpg", "https://example.com/img1.jpg"]
    })
    assert resp.status_code == 201
    item_id = resp.json()["id"]

    # 2) Add two reservation requests
    await ac.post(f"/listings/{item_id}/request/{TEST_USER_ID}")
    await ac.post(f"/listings/{item_id}/request/{OTHER_USER_ID}")

    # 3) Manually flip the listing to RESERVED and set buyerId in the test DB
    from backend.db.database import client
    test_db = client["nyu_marketplace_test"]
    await test_db.Listings.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": {
            "status": "reserved",
            "buyerId": ObjectId(TEST_USER_ID)
        }}
    )

    # 4) Fetch reservations—only the TEST_USER_ID request should be returned
    resp = await ac.get(f"/listings/{item_id}/reservations")
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1

    rv = data[0]
    assert rv["buyer_id"] == TEST_USER_ID
    assert rv["status"] == "confirmed"
    # ensure the timestamp fields were parsed back to ISO strings by the endpoint
    assert "requested_at" in rv and "expires_at" in rv