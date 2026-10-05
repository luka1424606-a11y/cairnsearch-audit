"""Persistence contract for identity/session data."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from .models import Principal


class IdentityRepository(Protocol):
    def get_principal_by_login(self, organization_id: UUID, login: str) -> Principal | None: ...
    def get_password_hash(self, organization_id: UUID, login: str) -> str | None: ...
    def create_session(
        self, session_id: UUID, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> None: ...
    def get_session_principal(self, session_id: UUID) -> Principal | None: ...
    def revoke_session(self, session_id: UUID) -> None: ...
