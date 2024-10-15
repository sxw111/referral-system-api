from app.models import PydanticBase


class TokenData(PydanticBase):
    id: int | None = None


class TokenResponse(PydanticBase):
    access_token: str
    token_type: str
