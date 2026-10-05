"""Identity domain value objects."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Principal:
    user_id: UUID
    organization_id: UUID
    login: str
    roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class SessionInfo:
    session_id: UUID
    user_id: UUID
    expires_at: datetime
