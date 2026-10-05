from unittest.mock import Mock

from cairnsearch.auth.rotation import SessionRotationService


def test_security_sensitive_change_can_revoke_current_session():
    repo = Mock()
    SessionRotationService(repo).revoke_current("opaque-token")
    repo.revoke_session_by_token_hash.assert_called_once_with("opaque-token")
