from fastapi import Response

from cairnsearch.auth.cookies import clear_session_cookie, set_session_cookie


def test_session_cookie_is_httponly_and_samesite():
    response = Response()
    set_session_cookie(response, "session-id")
    header = response.headers["set-cookie"]
    assert "HttpOnly" in header
    assert "SameSite=lax" in header


def test_session_cookie_can_be_cleared():
    response = Response()
    clear_session_cookie(response)
    assert "Max-Age=0" in response.headers["set-cookie"]
