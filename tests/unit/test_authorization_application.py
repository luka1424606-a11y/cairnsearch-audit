from unittest.mock import Mock
from uuid import uuid4

import pytest

from cairnsearch.authorization.application import AuthorizationApplicationService


def test_permissions_are_resolved_from_repository():
    repo = Mock()
    repo.get_permission_codes.return_value = frozenset({"document.read"})
    service = AuthorizationApplicationService(repo)
    user_id, org_id = uuid4(), uuid4()

    context = service.context_for_principal(user_id, org_id)

    assert context.permission_codes == frozenset({"document.read"})
    repo.get_permission_codes.assert_called_once_with(user_id, org_id)


def test_missing_permission_is_denied():
    repo = Mock()
    repo.get_permission_codes.return_value = frozenset()
    service = AuthorizationApplicationService(repo)

    with pytest.raises(PermissionError):
        service.require_permission(uuid4(), uuid4(), "admin.manage")


def test_required_permission_is_allowed():
    repo = Mock()
    repo.get_permission_codes.return_value = frozenset({"admin.manage"})
    service = AuthorizationApplicationService(repo)

    service.require_permission(uuid4(), uuid4(), "admin.manage")
