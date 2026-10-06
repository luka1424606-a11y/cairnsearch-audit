"""PostgreSQL persistence for deterministic legal citations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import text

from cairnsearch.platform.db import PostgresDatabase
from .citations import LegalCitation
from .citation_repository import LegalCitationRepository


class PostgresLegalCitationRepository(LegalCitationRepository):
    def __init__(self, database: PostgresDatabase):
        self._database = database

    def save(self, citation: LegalCitation) -> None:
        with self._database.transaction() as conn:
            conn.execute(
                text("""INSERT INTO legal_citation
                    (id, legal_version_id, provision_id, source_snapshot_id,
                     citation_key, locator, text_sha256, snapshot_sha256)
                    VALUES (:id,:version_id,:provision_id,:snapshot_id,
                            :citation_key,:locator,:text_sha256,:snapshot_sha256)
                    ON CONFLICT (legal_version_id, provision_id) DO UPDATE SET
                      citation_key=EXCLUDED.citation_key,
                      locator=EXCLUDED.locator,
                      text_sha256=EXCLUDED.text_sha256,
                      snapshot_sha256=EXCLUDED.snapshot_sha256"""),
                {
                    "id": citation.id,
                    "version_id": citation.legal_version_id,
                    "provision_id": citation.provision_id,
                    "snapshot_id": citation.source_snapshot_id,
                    "citation_key": citation.citation_key,
                    "locator": citation.locator,
                    "text_sha256": citation.text_sha256,
                    "snapshot_sha256": citation.snapshot_sha256,
                },
            )

    def get_by_key(self, citation_key: str) -> LegalCitation | None:
        with self._database.connection() as conn:
            row = conn.execute(
                text("""SELECT id, legal_version_id, provision_id, source_snapshot_id,
                        citation_key, locator, text_sha256, snapshot_sha256
                        FROM legal_citation WHERE citation_key=:key"""),
                {"key": citation_key},
            ).mappings().first()
        return self._map(row) if row else None

    def get_for_provision(self, provision_id: UUID) -> LegalCitation | None:
        with self._database.connection() as conn:
            row = conn.execute(
                text("""SELECT id, legal_version_id, provision_id, source_snapshot_id,
                        citation_key, locator, text_sha256, snapshot_sha256
                        FROM legal_citation WHERE provision_id=:id"""),
                {"id": provision_id},
            ).mappings().first()
        return self._map(row) if row else None

    @staticmethod
    def _map(row) -> LegalCitation:
        return LegalCitation(
            row["id"], row["legal_version_id"], row["provision_id"],
            row["source_snapshot_id"], row["citation_key"], row["locator"],
            row["text_sha256"], row["snapshot_sha256"],
        )
