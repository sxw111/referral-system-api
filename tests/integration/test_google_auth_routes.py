import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_google(client: AsyncClient):
    response = await client.get("/google/login")
    assert response.status_code in (
        status.HTTP_302_FOUND,
        status.HTTP_307_TEMPORARY_REDIRECT,
    )
    assert "https://accounts.google.com/o/oauth2/auth" in response.headers["location"]
