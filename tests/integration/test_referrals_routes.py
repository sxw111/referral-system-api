from datetime import datetime, timezone

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.config import settings


@pytest.mark.asyncio
async def test_get_referrals_with_existing_referrals(
    client: AsyncClient, test_db: AsyncSession, setup_cache
):
    user2 = User(email="testuser2@usertest.com", referer_id=1)
    user3 = User(email="testuser3@usertest.com", referer_id=1)

    test_db.add_all([user2, user3])
    await test_db.commit()

    referer_id = 1
    response = await client.get(f"/referrals/{referer_id}")

    users = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(users) == 2
    assert users[0]["email"] == "testuser2@usertest.com"
    assert users[1]["email"] == "testuser3@usertest.com"


@pytest.mark.asyncio
async def test_get_referrals_no_referrals(
    client: AsyncClient, test_db: AsyncSession, setup_cache
):
    referer_id = 1
    response = await client.get(f"/referrals/{referer_id}")

    msg = f"The user with id {referer_id} has no referrals."

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == msg


@pytest.mark.asyncio
async def test_get_referral_code_by_email_suc(
    client: AsyncClient, test_db: AsyncSession, setup_cache
):
    test_user = User(
        email="testuser@usertest.com",
        referral_code="testcode",
        referral_code_exp=datetime(
            2030, 11, 19, 12, 34, 31, 986056, tzinfo=timezone.utc
        ),
    )

    test_db.add(test_user)
    await test_db.commit()

    response = await client.get(f"/referrals/email/{test_user.email}/code")

    msg = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert msg.get("user_id") == 1
    assert msg.get("referral_code") == test_user.referral_code
    assert msg.get("is_expired") is False
    assert msg.get("referral_link") == (
        f"{settings.DOMAIN}{settings.API_V1_STR}"
        f"/auth/signup/referral/{test_user.referral_code}"
    )


@pytest.mark.asyncio
async def test_get_referral_code_by_email_no_user(
    client: AsyncClient, test_db: AsyncSession, setup_cache
):
    not_existing_email = "testemail@emailtest.com"

    response = await client.get(f"/referrals/email/{not_existing_email}/code")

    assert response.status_code == 404
    assert (
        response.json().get("detail") == "Referral code not found for the given email."
    )


@pytest.mark.asyncio
async def test_get_referral_code_by_email_user_exist_but_no_ref_code(
    client: AsyncClient, test_db: AsyncSession, setup_cache
):
    test_user = User(email="testemail@emailtest.com", referral_code=None)

    test_db.add(test_user)
    await test_db.commit()

    response = await client.get(f"/referrals/email/{test_user.email}/code")

    assert response.status_code == 404
    assert (
        response.json().get("detail") == "Referral code not found for the given email."
    )


@pytest.mark.asyncio
async def test_create_referral_code_success(client, current_user):
    response = await client.post("/referrals/code", json={"days": 30})

    assert response.status_code == 201
    assert response.json().get("referral_code") is not None
    assert response.json()["user_id"] == current_user.id


@pytest.mark.asyncio
async def test_delete_referral_code(client, current_user):
    response = await client.delete("/referrals/code")

    assert response.status_code == 200
    assert current_user.referral_code is None
