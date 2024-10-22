from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from fastapi_cache.decorator import cache
from pydantic import EmailStr

from app.auth.models import UserRead
from app.auth.service import CurrentUser
from app.auth.service import get_by_email as get_user_by_email
from app.auth.service import get_by_referral_code
from app.database.core import SessionDep

from .models import ReferralResponse
from .service import create, delete, get_referred_users_by_referer_id, set_referer_id

router = APIRouter()


@router.get("/{referer_id}", response_model=list[UserRead])
@cache(expire=60)
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
@cache(expire=10)
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
    "/code",
    response_model=ReferralResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_referral_code(
    db_session: SessionDep, current_user: CurrentUser, days: int = Query(30, ge=1)
) -> ReferralResponse:
    """Creates a referral code for the current user."""

    return await create(db_session=db_session, user_id=current_user.id, days=days)


@router.delete("/code", response_model=None)
async def delete_referral_code(
    db_session: SessionDep, current_user: CurrentUser
) -> None:
    """Deletes the referral code for the current user."""
    await delete(db_session=db_session, user_id=current_user.id)


@router.post("/code/apply", status_code=status.HTTP_201_CREATED)
async def use_referral_code(
    db_session: SessionDep, current_user: CurrentUser, referral_code: str
) -> dict[str, str]:
    """
    Uses a referral code for the current user if it has not been added already.
    """
    if current_user.referer_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already entered a referral code!",
        )

    referer = await get_by_referral_code(
        db_session=db_session, referral_code=referral_code
    )
    if not referer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Referral code not found!"
        )

    return await set_referer_id(
        db_session=db_session, user=current_user, referer_id=referer.id
    )
