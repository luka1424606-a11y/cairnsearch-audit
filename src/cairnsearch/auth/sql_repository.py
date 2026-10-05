"""SQL persistence adapter for identity/session data.

This is infrastructure code. Domain/application services depend on the
repository contract, not on SQL or PostgreSQL details.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from .models import Principal
from .repository import IdentityRepository


class PostgresIdentityRepository:
    def __init__(self, database):
        self._database = database

    def get_principal_by_login(self, organization_id: UUID, login: str) -> Principal | None:
        with self._database.connection() as conn:
            row = conn.execute(
                """
                SELECT u.id, u.organization_id, u.login,
                       COALESCE(array_agg(r.code) FILTER (WHERE r.code IS NOT NULL), '{}') AS roles
                FROM app_user u
                LEFT JOIN user_role ur ON ur.user_id = u.id
                LEFT JOIN role r ON r.id = ur.role_id
                WHERE u.organization_id = %s AND u.login = %s AND u.status = 'ACTIVE'
                GROUP BY u.id
                """,
                (organization_id, login),
            ).fetchone()
        if not row:
            return None
        return Principal(
            user_id=row["id"],
            organization_id=row["organization_id"],
            login=row["login"],
            roles=tuple(row["roles"] or ()),
        )

    def get_password_hash(self, organization_id: UUID, login: str) -> str | None:
        with self._database.connection() as conn:
            row = conn.execute(
                "SELECT password_hash FROM app_user WHERE organization_id = %s AND login = %s AND status = 'ACTIVE'",
                (organization_id, login),
            ).fetchone()
        return row["password_hash"] if row else None

    def create_session(self, session_id: UUID, user_id: UUID, token_hash: str, expires_at: datetime) -> None:
        with self._database.transaction() as conn:
            conn.execute(
                "INSERT INTO session (id, user_id, token_hash, expires_at) VALUES (%s, %s, %s, %s)",
                (session_id, user_id, token_hash, expires_at),
            )

    def get_session_principal(self, session_id: UUID) -> Principal | None:
        with self._database.connection() as conn:
            row = conn.execute(
                """
                SELECT s.id, s.expires_at, u.id AS user_id, u.organization_id, u.login,
                       COALESCE(array_agg(r.code) FILTER (WHERE r.code IS NOT NULL), '{}') AS roles
                FROM session s
                JOIN app_user u ON u.id = s.user_id
                LEFT JOIN user_role ur ON ur.user_id = u.id
                LEFT JOIN role r ON r.id = ur.role_id
                WHERE s.id = %s
                  AND s.revoked_at IS NULL
                  AND s.expires_at > CURRENT_TIMESTAMP
                  AND u.status = 'ACTIVE'
                GROUP BY s.id, s.expires_at, u.id
                """,
                (session_id,),
            ).fetchone()
        if not row:
            return None
        return Principal(
            user_id=row["user_id"],
            organization_id=row["organization_id"],
            login=row["login"],
            roles=tuple(row["roles"] or ()),
        )

    def revoke_session(self, session_id: UUID) -> None:
        with self._database.transaction() as conn:
            conn.execute(
                "UPDATE session SET revoked_at = CURRENT_TIMESTAMP WHERE id = %s",
                (session_id,),
            )
