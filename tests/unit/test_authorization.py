from uuid import uuid4

from cairnsearch.authorization.service import AuthorizationContext, AuthorizationService


def test_unknown_permission_is_denied():
    service = AuthorizationService()
    context = AuthorizationContext(uuid4(), uuid4(), frozenset({"document.read"}))
    assert not service.check_user_permission(context, "admin.manage")


def test_known_permission_is_allowed():
    service = AuthorizationService()
    context = AuthorizationContext(uuid4(), uuid4(), frozenset({"document.read"}))
    assert service.check_user_permission(context, "document.read")


def test_document_access_defaults_to_deny():
    service = AuthorizationService()
    context = AuthorizationContext(uuid4(), uuid4(), frozenset())
    assert not service.check_document_access(context, uuid4(), False)
