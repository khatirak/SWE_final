import pytest

# constants
TEST_USER_ID = "6812ab34fc012c5355f44c0e"
NON_EXISTENT_ID = "64f1c9a2e4b0c23b9f5e0a1b"  # valid ObjectId format, unlikely to exist
BAD_FORMAT_ID = "not-an-object-id"

@pytest.mark.asyncio
async def test_create_listing_with_two_images(ac):
    payload = {
        "title": "Image Count Test",
        "description": "Ensure images list works",
        "price": 50,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["images"],
        "location": "TestLoc",
        "images": ["https://example.com/1.jpg", "https://example.com/2.jpg"]
    }
    response = await ac.post("/listings/", json=payload)
    assert response.status_code == 201
    data = response.json()
    # ensure 'id' field (not '_id')
    assert "id" in data and isinstance(data["id"], str)
    # ensure exactly two images returned
    assert "images" in data
    assert isinstance(data["images"], list)
    assert len(data["images"]) == 2

@pytest.mark.asyncio
async def test_update_listing_status_nonexistent(ac):
    response = await ac.put(
        f"/listings/{NON_EXISTENT_ID}/status",
        params={"status": "reserved"}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_request_reservation_nonexistent_listing(ac):
    response = await ac.post(f"/listings/{NON_EXISTENT_ID}/request/{TEST_USER_ID}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_request_reservation_duplicate(ac):
    # create listing
    payload = {
        "title": "Duplicate Test",
        "description": "Testing duplicate reservation",
        "price": 100,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["dup"],
        "location": "TestLoc",
        "images": ["https://example.com/a.jpg", "https://example.com/b.jpg"]
    }
    create_resp = await ac.post("/listings/", json=payload)
    assert create_resp.status_code == 201
    item_id = create_resp.json()["id"]

    # first reservation request
    resp1 = await ac.post(f"/listings/{item_id}/request/{TEST_USER_ID}")
    assert resp1.status_code == 200

    # duplicate reservation should fail
    resp2 = await ac.post(f"/listings/{item_id}/request/{TEST_USER_ID}")
    assert resp2.status_code == 404

@pytest.mark.asyncio
async def test_confirm_reservation_bad_format_buyer_id(ac):
    # create listing
    payload = {
        "title": "Confirm Test",
        "description": "Test invalid confirm",
        "price": 90,
        "condition": "good",
        "category": "electronics_gadgets",
        "tags": ["confirm"],
        "location": "TestLoc",
        "images": ["https://example.com/x.jpg", "https://example.com/y.jpg"]
    }
    create_resp = await ac.post("/listings/", json=payload)
    assert create_resp.status_code == 201
    item_id = create_resp.json()["id"]

    # attempt to confirm with malformed buyer_id
    resp = await ac.post(
        f"/listings/{item_id}/confirm",
        json={"buyer_id": BAD_FORMAT_ID}
    )
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_get_reservations_nonexistent_listing(ac):
    response = await ac.get(f"/listings/{NON_EXISTENT_ID}/reservations")
    assert response.status_code == 200
    # as per implementation, returns empty list rather than 404
    assert response.json() == []

@pytest.mark.asyncio
async def test_cancel_reservation_no_existing_request(ac):
    # create listing
    payload = {
        "title": "Cancel Test",
        "description": "Test cancel without a request",
        "price": 75,
        "condition": "good",
        "category": "electronics_gadgets",
        "status": "available",
        "tags": ["cancel"],
        "location": "TestLoc",
        "images": ["https://example.com/p.jpg", "https://example.com/q.jpg"]
    }
    create_resp = await ac.post("/listings/", json=payload)
    assert create_resp.status_code == 201
    item_id = create_resp.json()["id"]

    # cancel without any prior reservation
    resp = await ac.delete(
        f"/listings/{item_id}/cancel_reservation",
        params={"buyer_id": TEST_USER_ID}
    )
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_cancel_reservation_nonexistent_listing(ac):
    resp = await ac.delete(
        f"/listings/{NON_EXISTENT_ID}/cancel_reservation",
        params={"buyer_id": TEST_USER_ID}
    )
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_mark_listing_as_sold_nonexistent(ac):
    resp = await ac.post(f"/listings/{NON_EXISTENT_ID}/sold")
    assert resp.status_code == 404