"""HTTP session authentication helpers.

The cookie contains only the opaque session token. Server-side repositories
resolve its hash to the authenticated principal.
"""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from .application import AuthenticationApplicationService
from .dependencies import SESSION_COOKIE


def require_principal(request: Request, auth_service: AuthenticationApplicationService):
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    principal = auth_service.principal_from_token(token)
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return principal
