"""I4.4 deterministic legal citations."""

from alembic import op
import sqlalchemy as sa

revision = "0008_legal_citations"
down_revision = "0007_legal_integrity"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "legal_citation",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("legal_version_id", sa.UUID(), sa.ForeignKey("legal_version.id"), nullable=False),
        sa.Column("provision_id", sa.UUID(), sa.ForeignKey("legal_provision.id"), nullable=False),
        sa.Column("source_snapshot_id", sa.UUID(), sa.ForeignKey("source_snapshot.id"), nullable=False),
        sa.Column("citation_key", sa.String(500), nullable=False, unique=True),
        sa.Column("locator", sa.String(500), nullable=False),
        sa.Column("text_sha256", sa.String(64), nullable=False),
        sa.Column("snapshot_sha256", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("legal_version_id", "provision_id", name="uq_legal_citation_provision"),
    )
    op.create_index("ix_legal_citation_version_locator", "legal_citation", ["legal_version_id", "locator"])
    op.create_check_constraint(
        "ck_legal_citation_text_sha256",
        "legal_citation",
        "text_sha256 ~ '^[0-9a-fA-F]{64}$'",
    )
    op.create_check_constraint(
        "ck_legal_citation_snapshot_sha256",
        "legal_citation",
        "snapshot_sha256 ~ '^[0-9a-fA-F]{64}$'",
    )


def downgrade():
    op.drop_constraint("ck_legal_citation_snapshot_sha256", "legal_citation")
    op.drop_constraint("ck_legal_citation_text_sha256", "legal_citation")
    op.drop_index("ix_legal_citation_version_locator", table_name="legal_citation")
    op.drop_table("legal_citation")
