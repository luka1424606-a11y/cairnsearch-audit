"""FastAPI authorization dependencies."""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from cairnsearch.auth.dependencies import authenticated_principal


def require_permission(permission: str):
    def dependency(request: Request, principal= None):
        principal = principal or authenticated_principal(request)
        service = getattr(request.app.state, "authorization_service", None)
        if service is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authorization unavailable")
        try:
            service.require_permission(
                principal.user_id,
                principal.organization_id,
                permission,
            )
        except PermissionError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden") from exc
        return principal

    return dependency
