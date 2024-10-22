from pydantic import Field
from app.models import PydanticBase

from app.config import settings


class ReferralResponse(PydanticBase):
    user_id: int
    referral_code: str
    is_expired: bool
    referral_link: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        self.referral_link = (
            f"{settings.DOMAIN}{settings.API_V1_STR}"
            f"/auth/signup/referral/{self.referral_code}"
        )
