from datetime import datetime, timedelta, timezone

from pydantic import EmailStr
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.core import Base
from app.models import PydanticBase
from app.referrals.utils import generate_random_referral_code


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(unique=False, nullable=True)
    referral_code: Mapped[str | None] = mapped_column(
        String(8), unique=True, nullable=True
    )
    referral_code_exp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    referer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    google_id: Mapped[str] = mapped_column(unique=True, index=True, nullable=True)

    def create_referral_code(self, days: int = 30) -> None:
        """Creates a referral code and determines its expiration date."""
        self.referral_code = generate_random_referral_code(8)
        self.referral_code_exp = datetime.now(timezone.utc) + timedelta(days=days)

    def delete_referral_code(self) -> None:
        """Deletes referral code."""
        self.referral_code = None
        self.referral_code_exp = None


class UserBase(PydanticBase):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    referer_referral_code: str | None


class UserUpdate(UserBase):
    email: str | None  # type: ignore
    password: str | None


class UserRead(UserBase):
    id: int
    email: str


class UserCreateGoogle(UserBase):
    google_id: str
