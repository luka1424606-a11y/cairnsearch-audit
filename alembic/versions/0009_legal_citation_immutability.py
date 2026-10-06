"""I4.4 immutable citations."""

from alembic import op

revision = "0009_legal_citation_immutable"
down_revision = "0008_legal_citations"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE FUNCTION prevent_legal_citation_mutation()
    RETURNS trigger AS $$
    BEGIN
        RAISE EXCEPTION 'legal_citation is immutable';
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_legal_citation_immutable
    BEFORE UPDATE OR DELETE ON legal_citation
    FOR EACH ROW EXECUTE FUNCTION prevent_legal_citation_mutation();
    """)


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS trg_legal_citation_immutable ON legal_citation")
    op.execute("DROP FUNCTION IF EXISTS prevent_legal_citation_mutation()")
