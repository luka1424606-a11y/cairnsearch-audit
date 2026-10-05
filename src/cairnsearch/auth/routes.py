"""Authentication route contracts.

The concrete router is kept separate from application services so HTTP policy
cannot leak into domain logic.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel

from .application import AuthenticationApplicationService
from .cookies import clear_session_cookie, set_session_cookie

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    organization_id: UUID
    login: str
    password: str


def login_response(
    service: AuthenticationApplicationService,
    response: Response,
    payload: LoginRequest,
    ttl: timedelta = timedelta(hours=8),
):
    expires_at = datetime.now(timezone.utc) + ttl
    result = service.authenticate(
        payload.organization_id,
        payload.login,
        payload.password,
        expires_at,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    session_id, token, principal = result
    set_session_cookie(response, str(session_id))
    return {"user_id": str(principal.user_id), "organization_id": str(principal.organization_id)}


def logout_response(
    service: AuthenticationApplicationService,
    response: Response,
    session_id: UUID,
):
    service.logout(session_id)
    clear_session_cookie(response)
    return {"status": "ok"}
