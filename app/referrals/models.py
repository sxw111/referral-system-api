from app.models import PydanticBase


class ReferralResponse(PydanticBase):
    user_id: int
    referral_code: str
    is_expired: bool
