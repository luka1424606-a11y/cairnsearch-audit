"""PostgreSQL authorization persistence adapter."""

from __future__ import annotations

from uuid import UUID


class PostgresAuthorizationRepository:
    def __init__(self, database):
        self._database = database

    def get_permission_codes(self, user_id: UUID, organization_id: UUID) -> frozenset[str]:
        with self._database.connection() as conn:
            rows = conn.execute(
                """
                SELECT DISTINCT p.code
                FROM app_user u
                JOIN user_role ur ON ur.user_id = u.id
                JOIN role_permission rp ON rp.role_id = ur.role_id
                JOIN permission p ON p.id = rp.permission_id
                WHERE u.id = %s
                  AND u.organization_id = %s
                  AND u.status = 'ACTIVE'
                """,
                (user_id, organization_id),
            ).fetchall()
        return frozenset(row["code"] for row in rows)
