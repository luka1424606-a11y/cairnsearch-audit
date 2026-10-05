"""PostgreSQL identity repository."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import text

from cairnsearch.platform.db import PostgresDatabase

from .models import Principal


class PostgresIdentityRepository:
    def __init__(self, database: PostgresDatabase):
        self._database = database

    def get_principal_by_login(self, organization_id: UUID, login: str) -> Principal | None:
        sql = text("""
            SELECT u.id, u.organization_id, u.login,
                   COALESCE(array_agg(r.code ORDER BY r.code) FILTER (WHERE r.code IS NOT NULL), '{}') AS roles
            FROM app_user u
            LEFT JOIN user_role ur ON ur.user_id = u.id
            LEFT JOIN role r ON r.id = ur.role_id
            WHERE u.organization_id = :organization_id
              AND u.login = :login
              AND u.status = 'ACTIVE'
            GROUP BY u.id, u.organization_id, u.login
        """)
        with self._database.connection() as conn:
            row = conn.execute(sql, {"organization_id": organization_id, "login": login}).mappings().first()
        if not row:
            return None
        return Principal(row["id"], row["organization_id"], row["login"], tuple(row["roles"] or ()))

    def get_password_hash(self, organization_id: UUID, login: str) -> str | None:
        sql = text("""
            SELECT password_hash
            FROM app_user
            WHERE organization_id = :organization_id
              AND login = :login
              AND status = 'ACTIVE'
        """)
        with self._database.connection() as conn:
            row = conn.execute(sql, {"organization_id": organization_id, "login": login}).first()
        return row[0] if row else None

    def create_session(self, session_id: UUID, user_id: UUID, token_hash: str, expires_at: datetime) -> None:
        sql = text("""
            INSERT INTO session (id, user_id, token_hash, expires_at)
            VALUES (:id, :user_id, :token_hash, :expires_at)
        """)
        with self._database.transaction() as conn:
            conn.execute(sql, {"id": session_id, "user_id": user_id, "token_hash": token_hash, "expires_at": expires_at})

    def get_session_principal_by_token_hash(self, token_hash: str) -> Principal | None:
        sql = text("""
            SELECT u.id, u.organization_id, u.login,
                   COALESCE(array_agg(r.code ORDER BY r.code) FILTER (WHERE r.code IS NOT NULL), '{}') AS roles
            FROM session s
            JOIN app_user u ON u.id = s.user_id
            LEFT JOIN user_role ur ON ur.user_id = u.id
            LEFT JOIN role r ON r.id = ur.role_id
            WHERE s.token_hash = :token_hash
              AND s.revoked_at IS NULL
              AND s.expires_at > CURRENT_TIMESTAMP
              AND u.status = 'ACTIVE'
            GROUP BY u.id, u.organization_id, u.login
        """)
        with self._database.connection() as conn:
            row = conn.execute(sql, {"token_hash": token_hash}).mappings().first()
        if not row:
            return None
        return Principal(row["id"], row["organization_id"], row["login"], tuple(row["roles"] or ()))

    def revoke_session_by_token_hash(self, token_hash: str) -> None:
        sql = text("UPDATE session SET revoked_at = CURRENT_TIMESTAMP WHERE token_hash = :token_hash AND revoked_at IS NULL")
        with self._database.transaction() as conn:
            conn.execute(sql, {"token_hash": token_hash})
