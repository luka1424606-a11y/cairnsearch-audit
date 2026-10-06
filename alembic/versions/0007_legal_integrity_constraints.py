"""I4.3 integrity constraints and snapshot immutability."""

from alembic import op
import sqlalchemy as sa

revision = "0007_legal_integrity"
down_revision = "0006_legal_immutability"
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        "ck_legal_version_dates",
        "legal_version",
        "effective_to IS NULL OR effective_from IS NULL OR effective_from <= effective_to",
    )
    op.create_check_constraint(
        "ck_legal_version_number_positive",
        "legal_version",
        "version_no > 0",
    )
    op.create_check_constraint(
        "ck_legal_provision_sequence_positive",
        "legal_provision",
        "sequence_no > 0",
    )
    op.create_check_constraint(
        "ck_legal_version_sha256",
        "legal_version",
        "content_sha256 ~ '^[0-9a-fA-F]{64}$'",
    )
    op.create_check_constraint(
        "ck_legal_provision_sha256",
        "legal_provision",
        "text_sha256 ~ '^[0-9a-fA-F]{64}$'",
    )
    op.create_check_constraint(
        "ck_source_snapshot_sha256",
        "source_snapshot",
        "content_sha256 ~ '^[0-9a-fA-F]{64}$'",
    )

    op.execute("""
    CREATE FUNCTION prevent_source_snapshot_mutation()
    RETURNS trigger AS $$
    BEGIN
        RAISE EXCEPTION 'source_snapshot is immutable';
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_source_snapshot_immutable
    BEFORE UPDATE OR DELETE ON source_snapshot
    FOR EACH ROW EXECUTE FUNCTION prevent_source_snapshot_mutation();
    """)


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS trg_source_snapshot_immutable ON source_snapshot")
    op.execute("DROP FUNCTION IF EXISTS prevent_source_snapshot_mutation()")
    op.drop_constraint("ck_source_snapshot_sha256", "source_snapshot")
    op.drop_constraint("ck_legal_provision_sha256", "legal_provision")
    op.drop_constraint("ck_legal_version_sha256", "legal_version")
    op.drop_constraint("ck_legal_provision_sequence_positive", "legal_provision")
    op.drop_constraint("ck_legal_version_number_positive", "legal_version")
    op.drop_constraint("ck_legal_version_dates", "legal_version")
