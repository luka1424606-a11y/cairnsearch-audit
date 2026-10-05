"""Internal document storage metadata and explicit ACL."""

from alembic import op
import sqlalchemy as sa

revision = "0004_internal_documents"
down_revision = "0003_seed_rbac"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "internal_document",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("organization_id", sa.UUID(), sa.ForeignKey("organization.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("document_type", sa.String(100), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("created_by", sa.UUID(), sa.ForeignKey("app_user.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_internal_document_org", "internal_document", ["organization_id"])

    op.create_table(
        "internal_document_version",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("document_id", sa.UUID(), sa.ForeignKey("internal_document.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(1000), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("mime_type", sa.String(255), nullable=False),
        sa.Column("byte_size", sa.BigInteger(), nullable=False),
        sa.Column("created_by", sa.UUID(), sa.ForeignKey("app_user.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("document_id", "version_no", name="uq_internal_document_version_no"),
    )
    op.create_index("ix_internal_document_version_document", "internal_document_version", ["document_id"])

    op.create_table(
        "internal_document_acl",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("document_id", sa.UUID(), sa.ForeignKey("internal_document.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.UUID(), sa.ForeignKey("role.id", ondelete="CASCADE"), nullable=False),
        sa.Column("can_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("document_id", "role_id", name="uq_internal_document_acl"),
    )

    op.create_table(
        "internal_document_audit",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("document_id", sa.UUID(), sa.ForeignKey("internal_document.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_id", sa.UUID(), sa.ForeignKey("internal_document_version.id"), nullable=True),
        sa.Column("actor_user_id", sa.UUID(), sa.ForeignKey("app_user.id"), nullable=False),
        sa.Column("operation", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("details_json", sa.Text(), nullable=True),
    )
    op.create_index("ix_internal_document_audit_document", "internal_document_audit", ["document_id", "created_at"])

def downgrade():
    op.drop_table("internal_document_audit")
    op.drop_table("internal_document_acl")
    op.drop_table("internal_document_version")
    op.drop_table("internal_document")
