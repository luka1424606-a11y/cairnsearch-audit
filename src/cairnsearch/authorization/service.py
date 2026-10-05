"""Default-deny authorization service contract."""

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
        return permission in context.permission_codes

    def check_document_access(
        self,
        context: AuthorizationContext,
        document_id: UUID,
        allowed: bool,
    ) -> bool:
        # The caller must supply an already-resolved ACL decision.
        # Unknown/failure states must be represented as False.
        return bool(allowed)

    def get_effective_scope(self, context: AuthorizationContext) -> UUID:
        return context.organization_id
