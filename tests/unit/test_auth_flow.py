from datetime import timedelta
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import Response

from cairnsearch.auth.application import AuthenticationApplicationService
from cairnsearch.auth.models import Principal
from cairnsearch.auth.passwords import hash_password
from cairnsearch.auth.routes import LoginRequest, login_response, logout_response


def test_login_sets_session_cookie():
    repo = Mock()
    org_id, user_id = uuid4(), uuid4()
    repo.get_password_hash.return_value = hash_password("secret")
    repo.get_principal_by_login.return_value = Principal(user_id, org_id, "alice", ("ADMIN",))
    response = Response()

    body = login_response(
        AuthenticationApplicationService(repo),
        response,
        LoginRequest(organization_id=org_id, login="alice", password="secret"),
    )

    assert body["user_id"] == str(user_id)
    assert "HttpOnly" in response.headers["set-cookie"]
    repo.create_session.assert_called_once()


def test_login_rejects_invalid_credentials():
    repo = Mock()
    repo.get_password_hash.return_value = hash_password("secret")
    response = Response()

    with pytest.raises(Exception) as exc:
        login_response(
            AuthenticationApplicationService(repo),
            response,
            LoginRequest(organization_id=uuid4(), login="alice", password="wrong"),
        )
    assert getattr(exc.value, "status_code", None) == 401


def test_logout_revokes_session_and_clears_cookie():
    service = Mock()
    response = Response()
    session_id = uuid4()

    logout_response(service, response, session_id)

    service.logout.assert_called_once_with(session_id)
    assert "Max-Age=0" in response.headers["set-cookie"]
