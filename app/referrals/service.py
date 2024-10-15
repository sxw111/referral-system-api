import secrets
import string

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.models import User
from app.auth.service import get as get_user

from .models import ReferralResponse


async def create(
    *, db_session: AsyncSession, user_id: int, days: int
) -> ReferralResponse:
    """Creates a referral code."""
    user = await get_user(db_session=db_session, user_id=user_id)

    user.create_referral_code(days=days)

    await db_session.commit()
    await db_session.refresh(user)

    return ReferralResponse(
        user_id=user.id, referral_code=user.referral_code, is_expired=False
    )


async def delete(*, db_session: AsyncSession, user_id: int) -> None:
    """Deletes the referral code."""
    user = await get_user(db_session=db_session, user_id=user_id)

    user.delete_referral_code()

    await db_session.commit()


async def get_referred_users_by_referer_id(
    *, db_session: AsyncSession, referer_id: int
) -> list[User] | None:
    """Returns a list of users referred by a specified referer."""
    query = select(User).where(User.referer_id == referer_id)

    result = await db_session.execute(query)

    return result.scalars().all()


def generate_random_referral_code(length: int) -> str:
    "Creates a unique code of a given length."
    characters = string.ascii_letters + string.digits

    return "".join(secrets.choice(characters) for _ in range(length))
