import httpx
from fastapi import APIRouter, status
from starlette.responses import RedirectResponse

from app.config import settings
from app.database.core import SessionDep
from app.jwt.models import TokenResponse
from app.security import create_access_token

from .models import UserCreateGoogle
from .service import create_user_through_google, get_by_email

google_auth_router = APIRouter()


@google_auth_router.get(
    "/login", response_class=RedirectResponse, status_code=status.HTTP_302_FOUND
)
async def login_google() -> RedirectResponse:
    """Redirects the user to the Google OAuth2 login page."""
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        "&scope=openid%20profile%20email&access_type=offline"
    )

    return RedirectResponse(google_auth_url)


@google_auth_router.get(
    "/auth/callback", response_model=TokenResponse, status_code=status.HTTP_200_OK
)
async def auth_google(db_session: SessionDep, code: str) -> TokenResponse:
    """Handles the Google OAuth2 callback and retrieves the access token."""
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        response_data = response.json()
        access_token = response_data.get("access_token")

        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        user_info = user_info_response.json()

        user = await get_by_email(db_session=db_session, email=user_info["email"])
        if not user:
            user_in = UserCreateGoogle(
                email=user_info["email"], google_id=user_info["id"]
            )

            user = await create_user_through_google(
                db_session=db_session, user_in=user_in
            )

        data = {"user_id": user.id}  # type: ignore
        access_token = create_access_token(data=data)

        return TokenResponse(access_token=access_token, token_type="bearer")
