from typing import TYPE_CHECKING
from datetime import datetime, timedelta

from pydantic import EmailStr
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.core import Base
from app.models import PydanticBase

if TYPE_CHECKING:
    from app.referrals.service import generate_random_referral_code


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(unique=False, nullable=False)
    referral_code: Mapped[str | None] = mapped_column(
        String(8), unique=True, nullable=True
    )
    referral_code_exp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    referer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    def create_referral_code(self, days: int = 30):
        "Creates a referral code and determines its expiration date."
        self.referral_code = generate_random_referral_code(8)
        self.referral_code_exp = datetime.utcnow() + timedelta(days=days)

    def delete_referral_code(self):
        """Deletes referral code."""
        self.referral_code = None
        self.referral_code_exp = None


class UserBase(PydanticBase):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    referer_referral_code: str | None


class UserUpdate(UserBase):
    email: str | None
    password: str | None


class UserRead(UserBase):
    id: int
    email: str
