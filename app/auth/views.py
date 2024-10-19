from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.config import settings
from app.database.core import SessionDep
from app.email import send_reset_email
from app.exceptions import PasswordResetTokenException
from app.jwt.models import TokenResponse
from app.security import (
    create_access_token,
    create_password_reset_token,
    verify_password,
)

from .models import (
    UserConfirmPassword,
    UserCreate,
    UserRead,
    UserResetPassword,
    UserUpdatePassword,
)
from .service import (
    CurrentUser,
    create,
    get_by_email,
    get_by_referral_code,
    update_password,
    verify_password_reset_token,
)
from .utils import verify_email_with_hunter

auth_router = APIRouter()
users_router = APIRouter()


@auth_router.post(
    "/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def signup(db_session: SessionDep, user_in: UserCreate) -> Any:
    """Creates a new user account."""
    user = await get_by_email(db_session=db_session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email `{user_in.email}` already exists.",
        )

    if not await verify_email_with_hunter(email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email address provided is not valid.",
        )

    referer_id = None
    if user_in.referer_referral_code is not None:
        referer = await get_by_referral_code(
            db_session=db_session, referral_code=user_in.referer_referral_code
        )
        if not referer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect referral code.",
            )
        referer_id = referer.id

    user = await create(db_session=db_session, user_in=user_in, referer_id=referer_id)

    return user


@auth_router.post(
    "/signin", response_model=TokenResponse, status_code=status.HTTP_200_OK
)
async def signin(
    db_session: SessionDep, user_credentials: OAuth2PasswordRequestForm = Depends()
) -> TokenResponse:
    """Authenticates a user and provides an access token."""
    user = await get_by_email(db_session=db_session, email=user_credentials.username)

    if user and verify_password(user_credentials.password, user.password):
        data = {"user_id": user.id}
        access_token = create_access_token(data=data)

        return TokenResponse(access_token=access_token, token_type="bearer")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )


@users_router.put("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    db_session: SessionDep, current_user: CurrentUser, password_in: UserUpdatePassword
) -> Any:
    """Changes the current user's password."""
    if not verify_password(password_in.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Old password isn't valid."
        )

    if password_in.new_password != password_in.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password confirmation doesn't match the password.",
        )

    return await update_password(
        db_session=db_session, user=current_user, new_password=password_in.new_password
    )

# For now, this is implemented as a simple prototype; in the future, 
# it will be implemented using background tasks.
@users_router.post("/reset-password")
async def request_reset_password(
    db_session: SessionDep, reset_data: UserResetPassword
) -> dict[str, str]:
    """Requests a password reset link for the user."""
    user = await get_by_email(db_session=db_session, email=reset_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    reset_token = create_password_reset_token({"sub": user.email})

    reset_link = f"{settings.DOMAIN}/reset-password/{reset_token}"

    subject = "Please reset your password"
    body = f"Click the link to reset your password: {reset_link}"

    await send_reset_email(reset_data.email, subject, body)

    return {"msg": "Password reset link has been sent to your email."}


@users_router.put("/reset-password/{token}")
async def reset_password(
    db_session: SessionDep,
    token: str,
    password_data: UserConfirmPassword,
) -> dict[str, str]:
    """Resets the user's password using a provided reset token."""
    email = await verify_password_reset_token(
        token=token, password_exception=PasswordResetTokenException()
    )

    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match."
        )

    user = await get_by_email(db_session=db_session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    await update_password(
        db_session=db_session, user=user, new_password=password_data.new_password
    )

    return {"msg": "Your password has been successfully reset!"}
