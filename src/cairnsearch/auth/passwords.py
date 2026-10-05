"""Password hashing policy."""

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError


_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("password must not be empty")
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False
