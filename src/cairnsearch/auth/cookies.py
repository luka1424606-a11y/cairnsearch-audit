"""Session cookie policy."""

from __future__ import annotations

from fastapi import Response

from .http import SESSION_COOKIE


def set_session_cookie(response: Response, session_id: str, secure: bool = False) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_id,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response, secure: bool = False) -> None:
    response.delete_cookie(
        key=SESSION_COOKIE,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )
