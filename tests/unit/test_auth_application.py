from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import Mock

from cairnsearch.auth.application import AuthenticationApplicationService
from cairnsearch.auth.models import Principal


def test_authentication_creates_session_after_valid_credentials():
    repo = Mock()
    user_id = uuid4()
    org_id = uuid4()
    repo.get_password_hash.return_value = "$argon2id$v=19$m=65536,t=3,p=4$example"
    # Use a real hash so verification is meaningful.
    from cairnsearch.auth.passwords import hash_password
    repo.get_password_hash.return_value = hash_password("correct")
    repo.get_principal_by_login.return_value = Principal(user_id, org_id, "alice", ("ADMIN",))

    service = AuthenticationApplicationService(repo)
    result = service.authenticate(
        org_id, "alice", "correct", datetime.now(timezone.utc) + timedelta(hours=1)
    )
    assert result is not None
    session_id, token, principal = result
    assert session_id and token and principal.user_id == user_id
    repo.create_session.assert_called_once()


def test_authentication_rejects_bad_password():
    repo = Mock()
    from cairnsearch.auth.passwords import hash_password
    repo.get_password_hash.return_value = hash_password("correct")
    service = AuthenticationApplicationService(repo)
    assert service.authenticate(
        uuid4(), "alice", "wrong", datetime.now(timezone.utc) + timedelta(hours=1)
    ) is None
