"""FastAPI authentication dependencies.

Application services are injected by the composition root, never constructed
implicitly by FastAPI.
"""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from .application import AuthenticationApplicationService

SESSION_COOKIE = "cairnsearch_session"


def authenticated_principal(request: Request) -> object:
    service = getattr(request.app.state, "auth_service", None)
    if service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication unavailable")

    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    principal = service.principal_from_token(token)
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return principal
