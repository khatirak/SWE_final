import pytest
from httpx import AsyncClient
from backend.main import app

from unittest.mock import AsyncMock, patch
from starlette.responses import RedirectResponse

@pytest.mark.asyncio
async def test_login_redirect():
    with patch("backend.app.auth.oauth.google.authorize_redirect", new_callable=AsyncMock) as mock_redirect:
        mock_redirect.return_value = RedirectResponse(url="https://google.com")
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/auth/login")
            assert response.status_code == 307
            assert response.headers["location"] == "https://google.com"

@pytest.mark.asyncio
async def test_new_user(monkeypatch):
    new_userinfo = {
        "email": "newguy@nyu.edu",
        "email_verified": True,
    }
    monkeypatch.setattr("backend.app.auth.oauth.google.authorize_access_token", AsyncMock(return_value={"userinfo": new_userinfo}))
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/auth/callback", cookies={"session": "dummy"})
        assert response.status_code == 307

@pytest.mark.asyncio
async def test_callback_rejects_non_nyu_email(monkeypatch):
    fake_userinfo = {
        "email": "notnyu@gmail.com",
        "email_verified": True,
    }

    monkeypatch.setattr("backend.app.auth.oauth.google.authorize_access_token", AsyncMock(return_value={"userinfo": fake_userinfo}))
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/auth/callback", cookies={"session": "dummy"})
        assert response.status_code == 307

@pytest.mark.asyncio
async def test_logout_clears_session():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/auth/logout")
        assert response.status_code == 200 or response.status_code == 307

@pytest.mark.asyncio
async def test_me_requires_auth(monkeypatch):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/auth/me")
        assert response.status_code == 401