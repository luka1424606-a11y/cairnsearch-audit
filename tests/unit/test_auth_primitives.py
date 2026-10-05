from datetime import datetime, timedelta, timezone
from uuid import uuid4

from cairnsearch.auth.passwords import hash_password, verify_password
from cairnsearch.auth.service import AuthenticationService
from cairnsearch.auth.tokens import hash_session_token


def test_password_hash_is_not_plaintext():
    password = "Test-only-password-123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(hashed, password)
    assert not verify_password(hashed, "wrong-password")


def test_session_token_is_opaque_and_hashed():
    service = AuthenticationService()
    session_id, token = service.create_session(
        uuid4(), datetime.now(timezone.utc) + timedelta(hours=1)
    )
    assert session_id
    assert token
    assert hash_session_token(token) != token
    assert service.token_digest(token) == hash_session_token(token)
