import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from app.api.main import app
import os


@pytest.mark.asyncio
async def test_signup_redirect():
    """
    Tests the '/signup' endpoint for correct HTTP behavior.

    The '/signup' endpoint must redirect the client to the Strava authorization page.

    Raises:
        AssertionError: If the response status is not 307 (Temporary Redirect)
        or if the 'Location' header is not the expected URL.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/signup")
        assert response.status_code == 307
        assert response.headers["location"].startswith(
            "http://www.strava.com/oauth/authorize"
        )


@pytest.mark.asyncio
async def test_signup_missing_strava_client_id(monkeypatch):
    """
    Tests the 'signup' endpoint with missing STRAVA_CLIENT_ID

    Args:
        monkeypatch (_pytest.monkeypatch.MonkeyPatch): pytest fixture
        that dynamically modifies environment variables
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        monkeypatch.delenv("STRAVA_CLIENT_ID", raising=False)
        response = await ac.get("/signup")
        assert response.status_code == 400
        assert response.json() == {"error": "Strava Client ID is required."}


@pytest.mark.asyncio
async def test_signup_missing_redirect_uri(monkeypatch):
    """
    Tests the 'signup' endpoint with missing STRAVA_REDIRECT_URI

    Args:
        monkeypatch (_pytest.monkeypatch.MonkeyPatch): pytest fixture
        that dynamically modifies environment variables
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        monkeypatch.delenv("STRAVA_REDIRECT_URI", raising=False)
        response = await ac.get("/signup")
        assert response.status_code == 400
        assert response.json() == {"error": "Could not find callback url."}


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["post", "delete", "put", "patch"])
async def test_signup_method_not_allowed(method):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        request = getattr(ac, method)
        response = await request("/signup")
        assert response.status_code == 405
    
@pytest.mark.asyncio
async def test_signup_injection_security(monkeypatch):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        monkeypatch.setenv("STRAVA_CLIENT_ID", "<script>alert('test')</script>")
        response = await ac.get("/signup")
        assert "<script>" not in response.headers.get("location")
        assert "%3Cscript%3E" in response.headers.get("location"), "Script tags should be percent-encoded in URLs"
