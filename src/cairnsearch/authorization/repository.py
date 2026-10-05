"""Authorization persistence contract."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID


class AuthorizationRepository(Protocol):
    def get_permission_codes(self, user_id: UUID, organization_id: UUID) -> frozenset[str]: ...
