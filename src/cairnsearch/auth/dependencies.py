"""FastAPI dependencies for authenticated application access."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status

from .application import AuthenticationApplicationService
from .http import SESSION_COOKIE


def authenticated_principal(
    request: Request,
    auth_service: AuthenticationApplicationService = Depends(),
):
    raw = request.cookies.get(SESSION_COOKIE)
    if not raw:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        from uuid import UUID
        session_id = UUID(raw)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required") from exc

    principal = auth_service.principal_from_session(session_id)
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return principal
