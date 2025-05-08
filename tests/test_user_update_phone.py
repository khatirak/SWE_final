import pytest
from fastapi import HTTPException, status

from backend.app.user import update_phone  # adjust import if your module path differs

# --- Dummy helpers to simulate Request, PhoneUpdate, and UserRepository ---

class DummyRequest:
    def __init__(self, session_data: dict):
        # Simulate Starlette Request.session
        self.session = session_data

class DummyPhoneData:
    def __init__(self, phoneNumber: str):
        # Matches PhoneUpdate.phoneNumber
        self.phoneNumber = phoneNumber

class SuccessfulRepo:
    async def update_phone(self, user_id: str, phone_number: str) -> bool:
        return True

class FailingRepo:
    async def update_phone(self, user_id: str, phone_number: str) -> bool:
        return False

# --- Tests ---

@pytest.mark.asyncio
async def test_update_phone_success():
    request = DummyRequest({'user': {'id': 'user123'}})
    phone_data = DummyPhoneData('1234567890')
    repo = SuccessfulRepo()

    result = await update_phone(phone_data, request, user_repo=repo)
    assert result == {"message": "Phone number updated successfully"}

@pytest.mark.asyncio
async def test_update_phone_unauthenticated():
    request = DummyRequest({})  # no 'user' in session
    phone_data = DummyPhoneData('1234567890')
    repo = SuccessfulRepo()

    with pytest.raises(HTTPException) as exc:
        await update_phone(phone_data, request, user_repo=repo)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Not authenticated"

@pytest.mark.asyncio
async def test_update_phone_user_not_found():
    request = DummyRequest({'user': {'id': 'user123'}})
    phone_data = DummyPhoneData('1234567890')
    repo = FailingRepo()

    with pytest.raises(HTTPException) as exc:
        await update_phone(phone_data, request, user_repo=repo)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "User not found or update failed"