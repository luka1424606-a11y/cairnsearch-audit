"""Authentication service contracts and primitives."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from .tokens import generate_session_token, hash_session_token


class AuthenticationService:
    """Infrastructure-neutral session token lifecycle.

    Persistence is deliberately injected; this module does not issue raw SQL.
    """

    def create_session(self, user_id: UUID, expires_at: datetime) -> tuple[UUID, str]:
        session_id = uuid4()
        token = generate_session_token()
        if expires_at.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware")
        if expires_at <= datetime.now(timezone.utc):
            raise ValueError("expires_at must be in the future")
        return session_id, token

    @staticmethod
    def token_digest(token: str) -> str:
        return hash_session_token(token)
