"""Permission policy helpers."""

from __future__ import annotations

from .service import AuthorizationContext


def context_from_principal(principal, permission_codes: frozenset[str]) -> AuthorizationContext:
    return AuthorizationContext(
        user_id=principal.user_id,
        organization_id=principal.organization_id,
        permission_codes=permission_codes,
    )
