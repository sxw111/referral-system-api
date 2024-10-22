import pytest
from datetime import datetime, timedelta, timezone

from app.auth.models import User
from app.referral.utils import generate_random_referral_code
from freezegun import freeze_time


@pytest.mark.unit
class TestModelsManager:
    """Test all the functions in the models module."""
    
    @pytest.mark.parametrize("days, expected_length", [(44, 8), (11, 8)])
    @freeze_time("2024-10-17 09:34:55")
    def test_create_referral_code(self, days, expected_length):
        """Test the creation of a referral code."""
        user = User()

        user.create_referral_code(days=days)

        assert user.referral_code is not None
        assert len(user.referral_code) == expected_length
        assert user.referral_code_exp == datetime.now(timezone.utc) + timedelta(days=days)


    def test_delete_referral_code(self):
        """Test the deletion of a referral code."""
        user = User()
        user.create_referral_code(days=30)

        user.delete_referral_code()

        assert user.referral_code is None
        assert user.referral_code_exp is None