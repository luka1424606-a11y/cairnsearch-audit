"""Authentication application service."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from .models import Principal
from .passwords import verify_password
from .repository import IdentityRepository
from .service import AuthenticationService


class AuthenticationApplicationService:
    def __init__(self, repository: IdentityRepository, sessions: AuthenticationService | None = None):
        self._repository = repository
        self._sessions = sessions or AuthenticationService()

    def authenticate(self, organization_id: UUID, login: str, password: str, expires_at: datetime):
        password_hash = self._repository.get_password_hash(organization_id, login)
        if not password_hash or not verify_password(password_hash, password):
            return None
        principal = self._repository.get_principal_by_login(organization_id, login)
        if not principal:
            return None
        session_id, token = self._sessions.create_session(principal.user_id, expires_at)
        self._repository.create_session(
            session_id, principal.user_id, self._sessions.token_digest(token), expires_at
        )
        return session_id, token, principal

    def principal_from_token(self, token: str) -> Principal | None:
        return self._repository.get_session_principal_by_token_hash(self._sessions.token_digest(token))

    def logout(self, token: str) -> None:
        self._repository.revoke_session_by_token_hash(self._sessions.token_digest(token))
