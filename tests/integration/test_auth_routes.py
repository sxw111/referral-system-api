import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.security import verify_password


@pytest.mark.asyncio
async def test_signup_new_user(client: AsyncClient, test_db: AsyncSession):
    post_body = {
        "email": "alexm123@gmail.com",
        "password": "test123",
        "referer_referral_code": None,
    }

    response = await client.post("/auth/signup", json=post_body)

    assert response.status_code == status.HTTP_201_CREATED

    user_from_db = await test_db.get(User, 1)

    if user_from_db is None:
        pytest.fail("User was not added to the database")

    assert user_from_db.email == post_body["email"]
    assert verify_password(post_body["password"], user_from_db.password)
