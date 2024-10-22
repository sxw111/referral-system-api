from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings
from app.database.core import SessionDep
from app.exceptions import CredentialsException, PasswordResetTokenException
from app.jwt.models import TokenData
from app.security import get_password_hash

from .models import User, UserCreate, UserCreateByLink, UserCreateGoogle


async def get(*, db_session: AsyncSession, user_id: int) -> User | None:
    """Returns a user based on the given id."""
    result = await db_session.execute(select(User).where(User.id == user_id))

    return result.scalars().first()


async def get_by_email(*, db_session: AsyncSession, email: EmailStr) -> User | None:
    """Returns a user by its email."""
    query = select(User).where(User.email == email)

    result = await db_session.execute(query)

    return result.scalars().first()


async def get_by_referral_code(
    *, db_session: AsyncSession, referral_code: str
) -> User | None:
    """
    Returns the user by his referral code if it
    exists and its expiration date has not expired.
    """
    query = select(User).where(User.referral_code == referral_code)
    result = await db_session.execute(query)

    user = result.scalars().first()

    if user:
        if user.referral_code_exp is None or user.referral_code_exp < datetime.now(
            timezone.utc
        ):
            return None

    return user


async def create(
    *,
    db_session: AsyncSession,
    user_in: UserCreate | UserCreateByLink,
    referer_id: int | None
) -> User:
    """Creates a new user."""
    hashed_password = get_password_hash(user_in.password)
    user_in.password = hashed_password

    user = User(
        **user_in.model_dump(exclude={"referer_referral_code"}), referer_id=referer_id
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


async def create_user_through_google(
    *, db_session: AsyncSession, user_in: UserCreateGoogle
) -> User:
    """
    Creates a new user in the database using
    information retrieved from Google OAuth.
    """
    user = User(**user_in.model_dump())

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


async def update_password(
    db_session: AsyncSession, user: User, new_password: str
) -> dict[str, str]:
    """Updates the user's password."""
    user.password = get_password_hash(new_password)

    await db_session.commit()
    await db_session.refresh(user)

    return {"msg": "The password has been successfully changed."}


async def verify_access_token(
    token: str, credentials_exception: CredentialsException
) -> TokenData:
    """Verifies and decodes the provided JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except JWTError:
        raise credentials_exception

    return token_data


oauth2_scheme_v1 = OAuth2PasswordBearer(tokenUrl="api/v1/auth/signin")


async def get_current_user(
    db: SessionDep, token: Annotated[str, Depends(oauth2_scheme_v1)]
) -> User:
    """Retrieves the current user based on the provided JWT access token."""
    token_data = await verify_access_token(token, CredentialsException())

    result = await db.execute(select(User).where(User.id == token_data.id))
    user = result.scalars().first()

    if user is None:
        raise CredentialsException()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def verify_password_reset_token(
    token: str,
    password_exception: PasswordResetTokenException,
) -> EmailStr:
    """Verifies the password reset token and extracts the user's email address."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "password_reset":
            raise password_exception

        email = payload.get("sub")
        if not email:
            raise password_exception

    except JWTError:
        raise password_exception

    return email
