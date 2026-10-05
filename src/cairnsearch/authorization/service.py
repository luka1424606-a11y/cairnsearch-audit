"""Default-deny authorization service."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AuthorizationContext:
    user_id: UUID
    organization_id: UUID
    permission_codes: frozenset[str]


class AuthorizationService:
    def check_user_permission(self, context: AuthorizationContext, permission: str) -> bool:
        if not permission or context is None:
            return False
        return permission in context.permission_codes

    def check_document_access(
        self,
        context: AuthorizationContext,
        document_id: UUID,
        allowed: bool,
    ) -> bool:
        if context is None or document_id is None:
            return False
        return bool(allowed)

    def get_effective_scope(self, context: AuthorizationContext) -> UUID:
        if context is None:
            raise PermissionError("authorization context is required")
        return context.organization_id
