"""I4 Belarus legal knowledge domain: immutable versions, provisions and source lineage."""

from alembic import op
import sqlalchemy as sa

revision = "0005_legal_knowledge"
down_revision = "0004_internal_documents"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "official_source",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("base_url", sa.String(1000), nullable=False),
        sa.Column("jurisdiction", sa.String(10), nullable=False, server_default="BY"),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "legal_document",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("jurisdiction", sa.String(10), nullable=False, server_default="BY"),
        sa.Column("document_type", sa.String(80), nullable=False),
        sa.Column("identifier", sa.String(300), nullable=False),
        sa.Column("title", sa.String(1000), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("jurisdiction", "identifier", name="uq_legal_document_identifier"),
    )

    op.create_table(
        "legal_version",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("legal_document_id", sa.UUID(), sa.ForeignKey("legal_document.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.UUID(), sa.ForeignKey("official_source.id"), nullable=False),
        sa.Column("source_locator", sa.String(2000), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("publication_date", sa.Date(), nullable=True),
        sa.Column("effective_from", sa.Date(), nullable=True),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("verification_status", sa.String(32), nullable=False, server_default="UNVERIFIED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("legal_document_id", "version_no", name="uq_legal_version_no"),
    )
    op.create_index("ix_legal_version_effective", "legal_version", ["legal_document_id", "effective_from", "effective_to"])

    op.create_table(
        "source_snapshot",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("source_id", sa.UUID(), sa.ForeignKey("official_source.id"), nullable=False),
        sa.Column("legal_version_id", sa.UUID(), sa.ForeignKey("legal_version.id", ondelete="CASCADE"), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("source_url", sa.String(2000), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("storage_key", sa.String(1000), nullable=False),
        sa.Column("retrieval_status", sa.String(32), nullable=False, server_default="CAPTURED"),
        sa.UniqueConstraint("legal_version_id", "content_sha256", name="uq_source_snapshot_hash"),
    )

    op.create_table(
        "legal_provision",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("legal_version_id", sa.UUID(), sa.ForeignKey("legal_version.id", ondelete="CASCADE"), nullable=False),
        sa.Column("locator", sa.String(500), nullable=False),
        sa.Column("heading", sa.String(1000), nullable=True),
        sa.Column("text_sha256", sa.String(64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.UniqueConstraint("legal_version_id", "locator", name="uq_legal_provision_locator"),
    )

    op.create_table(
        "legal_document_relation",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("from_document_id", sa.UUID(), sa.ForeignKey("legal_document.id", ondelete="CASCADE"), nullable=False),
        sa.Column("to_document_id", sa.UUID(), sa.ForeignKey("legal_document.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relation_type", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("from_document_id", "to_document_id", "relation_type", name="uq_legal_document_relation"),
    )

    op.create_table(
        "legal_resolution",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("legal_document_id", sa.UUID(), sa.ForeignKey("legal_document.id", ondelete="CASCADE"), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("legal_version_id", sa.UUID(), sa.ForeignKey("legal_version.id"), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("legal_document_id", "as_of_date", name="uq_legal_resolution_date"),
    )

    op.create_index("ix_legal_provision_version", "legal_provision", ["legal_version_id", "sequence_no"])
    op.create_index("ix_source_snapshot_version", "source_snapshot", ["legal_version_id"])


def downgrade():
    op.drop_table("legal_resolution")
    op.drop_table("legal_document_relation")
    op.drop_table("legal_provision")
    op.drop_table("source_snapshot")
    op.drop_table("legal_version")
    op.drop_table("legal_document")
    op.drop_table("official_source")
