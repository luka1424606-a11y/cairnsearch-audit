"""Authentication HTTP contracts."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel

from .application import AuthenticationApplicationService
from .cookies import clear_session_cookie, set_session_cookie

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    organization_id: UUID
    login: str
    password: str


def login_response(service: AuthenticationApplicationService, response: Response, payload: LoginRequest,
                   ttl: timedelta = timedelta(hours=8)):
    result = service.authenticate(
        payload.organization_id,
        payload.login,
        payload.password,
        datetime.now(timezone.utc) + ttl,
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    _, token, principal = result
    set_session_cookie(response, token)
    return {"user_id": str(principal.user_id), "organization_id": str(principal.organization_id)}


def logout_response(service: AuthenticationApplicationService, request: Request, response: Response):
    token = request.cookies.get("cairnsearch_session")
    if token:
        service.logout(token)
    clear_session_cookie(response)
    return {"status": "ok"}
