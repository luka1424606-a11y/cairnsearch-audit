"""Session rotation contract for security-sensitive privilege changes."""

from __future__ import annotations

from .repository import IdentityRepository


class SessionRotationService:
    def __init__(self, repository: IdentityRepository):
        self._repository = repository

    def revoke_current(self, token: str) -> None:
        self._repository.revoke_session_by_token_hash(token)
