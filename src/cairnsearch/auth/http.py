"""HTTP session authentication helpers."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, Request, status

from .application import AuthenticationApplicationService


SESSION_COOKIE = "cairnsearch_session"


def require_principal(request: Request, auth_service: AuthenticationApplicationService):
    raw = request.cookies.get(SESSION_COOKIE)
    if not raw:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        session_id = UUID(raw)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required") from exc

    principal = auth_service.principal_from_session(session_id)
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return principal


def require_permission(principal, authorization_service, permission: str, permission_codes: frozenset[str]):
    from .authorization_adapter import authorization_context

    context = authorization_context(principal, permission_codes)
    if not authorization_service.check_user_permission(context, permission):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return principal
