"""I1 foundation: UUID support and append-only audit foundation."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_event",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("organization_id", UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("request_id", UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(200), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", UUID(as_uuid=True), nullable=True),
        sa.Column("agent_code", sa.String(100), nullable=True),
        sa.Column("decision", sa.String(100), nullable=True),
        sa.Column("policy_version", sa.String(100), nullable=True),
        sa.Column("model_provider", sa.String(100), nullable=True),
        sa.Column("model_name", sa.String(200), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
    )
    op.create_index("ix_audit_event_timestamp", "audit_event", ["timestamp"])
    op.create_index("ix_audit_event_request_id", "audit_event", ["request_id"])
    op.create_index(
        "ix_audit_event_resource",
        "audit_event",
        ["resource_type", "resource_id"],
    )

    # pgvector is optional. Retrieval migrations will verify availability
    # before creating vector storage.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        try:
            bind.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
        except Exception:
            pass


def downgrade() -> None:
    op.drop_index("ix_audit_event_resource", table_name="audit_event")
    op.drop_index("ix_audit_event_request_id", table_name="audit_event")
    op.drop_index("ix_audit_event_timestamp", table_name="audit_event")
    op.drop_table("audit_event")
