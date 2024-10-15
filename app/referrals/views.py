from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from pydantic import EmailStr

from app.auth.models import UserRead
from app.auth.service import CurrentUser
from app.auth.service import get_by_email as get_user_by_email
from app.database.core import SessionDep

from .models import ReferralResponse
from .service import create, delete, get_referred_users_by_referer_id

router = APIRouter()


@router.get("/{referer_id}/referrals", response_model=list[UserRead])
@cache(expire=300)
async def get_refferals(db_session: SessionDep, referer_id: int) -> Any:
    """Retrieves all referrals associated with a given referer ID."""
    return await get_referred_users_by_referer_id(
        db_session=db_session, referer_id=referer_id
    )


@router.get(
    "/email/{email}/code",
    response_model=ReferralResponse,
    status_code=status.HTTP_200_OK,
)
@cache(expire=300)
async def get_referral_code_by_email(
    db_session: SessionDep, email: EmailStr
) -> ReferralResponse:
    """Retrieves the referral code for a user by their email."""
    referer = await get_user_by_email(db_session=db_session, email=email)

    if referer is None or referer.referral_code is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral code not found for the given email.",
        )

    is_expired = referer.referral_code_exp < datetime.now(timezone.utc)  # type: ignore

    return ReferralResponse(
        user_id=referer.id, referral_code=referer.referral_code, is_expired=is_expired
    )


@router.post(
    "/generate-referral-code",
    response_model=ReferralResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_referral_code(
    db_session: SessionDep, current_user: CurrentUser, days: int = Query(30, ge=1)
) -> ReferralResponse:
    """Creates a referral code for the current user."""
    cache_key_email = f"/api/v1/referrals/email/{current_user.email}/code"
    await FastAPICache.clear(cache_key_email)

    return await create(db_session=db_session, user_id=current_user.id, days=days)


@router.delete("/delete-referral-code", response_model=None)
async def delete_referral_code(
    db_session: SessionDep, current_user: CurrentUser
) -> None:
    """Deletes the referral code for the current user."""
    await delete(db_session=db_session, user_id=current_user.id)
