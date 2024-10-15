import secrets
import string


def generate_random_referral_code(length: int) -> str:
    "Creates a unique code of a given length."
    characters = string.ascii_letters + string.digits

    return "".join(secrets.choice(characters) for _ in range(length))
