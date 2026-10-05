"""FastAPI authorization dependencies."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status

from cairnsearch.auth.dependencies import authenticated_principal
from .application import AuthorizationApplicationService


def require_permission(permission: str):
    def dependency(
        principal=Depends(authenticated_principal),
        service: AuthorizationApplicationService = Depends(),
    ):
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
