"""Authorization application service."""

from __future__ import annotations

from uuid import UUID

from .repository import AuthorizationRepository
from .service import AuthorizationContext, AuthorizationService


class AuthorizationApplicationService:
    def __init__(
        self,
        repository: AuthorizationRepository,
        policy: AuthorizationService | None = None,
    ):
        self._repository = repository
        self._policy = policy or AuthorizationService()

    def context_for_principal(self, user_id: UUID, organization_id: UUID) -> AuthorizationContext:
        permissions = self._repository.get_permission_codes(user_id, organization_id)
        return AuthorizationContext(
            user_id=user_id,
            organization_id=organization_id,
            permission_codes=permissions,
        )

    def require_permission(self, user_id: UUID, organization_id: UUID, permission: str) -> None:
        context = self.context_for_principal(user_id, organization_id)
        if not self._policy.check_user_permission(context, permission):
            raise PermissionError("forbidden")
