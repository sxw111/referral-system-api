import string

import pytest

from app.referral.utils import generate_random_referral_code


@pytest.mark.unit
class TestUtilsManager:
    """Test all the functions in the utils module."""

    def test_generate_random_referral_code_length(self):
        """Test if the generated referral code has the correct length."""
        length = 8
        code = generate_random_referral_code(length)
        assert len(code) == length

    def test_generate_random_referral_code_content(self):
        """Test if the generated referral code contains only valid characters."""
        length = 12
        code = generate_random_referral_code(length)
        valid_characters = string.ascii_letters + string.digits
        assert all(char in valid_characters for char in code)

    def test_generate_random_referral_code_uniqueness(self):
        """Test for uniqueness of codes during multiple calls."""
        codes = {generate_random_referral_code(10) for _ in range(100)}

        assert len(codes) == 100
