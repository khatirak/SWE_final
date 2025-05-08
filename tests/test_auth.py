import pytest
from httpx import AsyncClient
from backend.main import app
import asyncio
from datetime import datetime
from fastapi import HTTPException, status

from starlette.requests import Request
from starlette.responses import RedirectResponse
from backend.app.auth import (
    login, auth_callback, logout, get_current_user,
    oauth
)
from authlib.integrations.starlette_client import OAuthError

from unittest.mock import AsyncMock, patch

class DummyRequest(Request):
    def __init__(self, scope, session=None):
        super().__init__(scope)
        self._session = session or {}
    @property
    def session(self):
        return self._session

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


@pytest.mark.asyncio
async def test_login_exception(monkeypatch):
    dummy = DummyRequest({"type": "http"})
    async def raise_error(req, uri):
        raise RuntimeError("fail")
    monkeypatch.setattr(oauth.google, 'authorize_redirect', raise_error)
    with pytest.raises(HTTPException) as exc:
        await login(dummy)
    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

@pytest.mark.asyncio
async def test_auth_callback_oauth_error(monkeypatch):
    dummy = DummyRequest({"type": "http"})
    async def raise_oauth(req): raise OAuthError("o")
    monkeypatch.setattr(oauth.google, 'authorize_access_token', raise_oauth)
    resp = await auth_callback(dummy, db=None)
    assert isinstance(resp, RedirectResponse)
    assert "error=oauth_error" in resp.headers['location']

@pytest.mark.asyncio
async def test_logout_success():
    sess = {'user': {'id':'u'}}
    dummy = DummyRequest({"type": "http"}, session=sess)
    resp = await logout(dummy)
    assert isinstance(resp, RedirectResponse)
    assert resp.headers['location'].endswith('://localhost:3000')
    assert dummy.session == {}

@pytest.mark.asyncio
async def test_get_current_user_success_and_fail(monkeypatch):
    sess = {'user': {'id':'uid'}}
    dummy = DummyRequest({"type": "http"}, session=sess)
    class FakeRepo:
        def __init__(self, db): pass
        async def get_user_by_id(self, uid): return type('U', (), {'id':uid,'email':'e','name':'n','phone':None})()
    monkeypatch.setattr('backend.app.auth.UserRepository', FakeRepo)
    user = await get_current_user(dummy, db=None)
    assert user.id == 'uid'
    # no session
    dummy2 = DummyRequest({"type": "http"})
    with pytest.raises(HTTPException) as exc2:
        await get_current_user(dummy2, db=None)
    assert exc2.value.status_code == status.HTTP_401_UNAUTHORIZED
    # user not found
    dummy3 = DummyRequest({"type": "http"}, session=sess)
    class FakeRepo2(FakeRepo):
        async def get_user_by_id(self, uid): return None
    monkeypatch.setattr('backend.app.auth.UserRepository', FakeRepo2)
    with pytest.raises(HTTPException) as exc3:
        await get_current_user(dummy3, db=None)
    assert exc3.value.status_code == status.HTTP_404_NOT_FOUND
