"""Seed deterministic initial roles and permissions."""

from alembic import op
import sqlalchemy as sa

revision = "0003_seed_rbac"
down_revision = "0002_identity_access"
branch_labels = None
depends_on = None

ROLES = {
    "ADMIN": "00000000-0000-0000-0000-000000000001",
    "LEGAL": "00000000-0000-0000-0000-000000000002",
    "HR": "00000000-0000-0000-0000-000000000003",
    "OCCUPATIONAL_SAFETY": "00000000-0000-0000-0000-000000000004",
    "EMPLOYEE": "00000000-0000-0000-0000-000000000005",
}

PERMISSIONS = {
    "auth.login": "00000000-0000-0000-0001-000000000001",
    "auth.logout": "00000000-0000-0000-0001-000000000002",
    "users.read": "00000000-0000-0000-0001-000000000003",
    "users.manage": "00000000-0000-0000-0001-000000000004",
    "documents.read": "00000000-0000-0000-0001-000000000005",
    "documents.manage": "00000000-0000-0000-0001-000000000006",
    "legal.read": "00000000-0000-0000-0001-000000000007",
    "hr.read": "00000000-0000-0000-0001-000000000008",
    "safety.read": "00000000-0000-0000-0001-000000000009",
}

ROLE_PERMISSIONS = {
    "ADMIN": tuple(PERMISSIONS),
    "LEGAL": ("auth.login", "auth.logout", "documents.read", "legal.read"),
    "HR": ("auth.login", "auth.logout", "documents.read", "hr.read"),
    "OCCUPATIONAL_SAFETY": ("auth.login", "auth.logout", "documents.read", "safety.read"),
    "EMPLOYEE": ("auth.login", "auth.logout", "documents.read"),
}


def upgrade():
    for code, rid in ROLES.items():
        op.execute(
            sa.text("""
                INSERT INTO role (id, code, name)
                VALUES (:id, :code, :name)
                ON CONFLICT (code) DO NOTHING
            """).bindparams(id=rid, code=code, name=code)
        )

    for code, pid in PERMISSIONS.items():
        op.execute(
            sa.text("""
                INSERT INTO permission (id, code, description)
                VALUES (:id, :code, :description)
                ON CONFLICT (code) DO NOTHING
            """).bindparams(id=pid, code=code, description=code)
        )

    for role_code, permission_codes in ROLE_PERMISSIONS.items():
        for permission_code in permission_codes:
            op.execute(
                sa.text("""
                    INSERT INTO role_permissions (role_id, permission_id)
                    SELECT r.id, p.id
                    FROM role r CROSS JOIN permission p
                    WHERE r.code=:role_code AND p.code=:permission_code
                    ON CONFLICT DO NOTHING
                """).bindparams(
                    role_code=role_code,
                    permission_code=permission_code,
                )
            )


def downgrade():
    for role_code in ROLES:
        op.execute(
            sa.text("""
                DELETE FROM role_permissions
                WHERE role_id=(SELECT id FROM role WHERE code=:role_code)
            """).bindparams(role_code=role_code)
        )
    for code in PERMISSIONS:
        op.execute(
            sa.text("DELETE FROM permission WHERE code=:code").bindparams(code=code)
        )
    for code in ROLES:
        op.execute(
            sa.text("DELETE FROM role WHERE code=:code").bindparams(code=code)
        )
