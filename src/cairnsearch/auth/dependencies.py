"""FastAPI dependencies for authenticated application access."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status

from .application import AuthenticationApplicationService
from .http import SESSION_COOKIE


def authenticated_principal(
    request: Request,
    auth_service: AuthenticationApplicationService = Depends(),
):
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    principal = auth_service.principal_from_token(token)
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return principal
