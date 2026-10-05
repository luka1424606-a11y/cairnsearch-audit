from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from cairnsearch.auth.http import require_principal, require_permission
from cairnsearch.auth.models import Principal


def request_with_cookie(value: str | None):
    headers = []
    if value is not None:
        headers.append((b"cookie", f"cairnsearch_session={value}".encode()))
    return Request({"type": "http", "method": "GET", "path": "/", "headers": headers})


def test_missing_session_is_denied():
    request = request_with_cookie(None)
    with pytest.raises(HTTPException) as exc:
        require_principal(request, Mock())
    assert exc.value.status_code == 401


def test_invalid_session_id_is_denied():
    request = request_with_cookie("not-a-uuid")
    with pytest.raises(HTTPException) as exc:
        require_principal(request, Mock())
    assert exc.value.status_code == 401


def test_valid_session_returns_principal():
    request = request_with_cookie(str(uuid4()))
    principal = Principal(uuid4(), uuid4(), "alice", ("ADMIN",))
    service = Mock()
    service.principal_from_session.return_value = principal
    assert require_principal(request, service) == principal


def test_missing_permission_is_forbidden():
    principal = Principal(uuid4(), uuid4(), "alice", ("EMPLOYEE",))
    with pytest.raises(HTTPException) as exc:
        require_permission(principal, Mock(), "admin.manage", frozenset())
    assert exc.value.status_code == 403


def test_allowed_permission_passes():
    principal = Principal(uuid4(), uuid4(), "alice", ("ADMIN",))
    authz = Mock()
    authz.check_user_permission.return_value = True
    assert require_permission(
        principal, authz, "admin.manage", frozenset({"admin.manage"})
    ) == principal
