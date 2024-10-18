import httpx
from fastapi import HTTPException, status
from pydantic import EmailStr

from app.config import settings


async def verify_email_with_hunter(email: EmailStr) -> bool:
    async with httpx.AsyncClient() as client:
        """
        Sending a request to the hunter.io service to verify the email
        entered by the user. All results except 'undeliverable' will return True,
        which will indicate that the email is available for registration.

        The verification result indicates the status of the email address:
        - 'deliverable': email address is valid.
        - 'undeliverable': the email address is not valid.
        - 'risky': the verification can't be validated.

        For more details, refer to the Hunter.io documentation:
        https://hunter.io/api-documentation#email-verifier
        """
        params = {"email": email, "api_key": settings.HUNTER_IO_API_KEY}
        response = await client.get(
            "https://api.hunter.io/v2/email-verifier", params=params
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify email with Hunter.io",
            )

        data = response.json()
        result = data.get("data", {}).get("result")

        if result == "undeliverable":
            return False

        return True
