"""PostgreSQL implementation of atomic legal publication."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import text

from cairnsearch.platform.db import PostgresDatabase
from .models import LegalProvision, LegalVersion, VerificationStatus
from .publication_repository import LegalPublicationRepository
from .publishing import PublicationDraft


class PostgresLegalPublicationRepository(LegalPublicationRepository):
    def __init__(self, database: PostgresDatabase, snapshot_store):
        self._database = database
        self._snapshot_store = snapshot_store

    def publish(self, draft: PublicationDraft) -> UUID:
        version = draft.version
        snapshot_id = uuid4()
        storage_key = f"legal/{version.id}/source"
        if self._snapshot_store.put_if_absent(storage_key, draft.source_content) is False:
            raise RuntimeError("source snapshot already exists")

        try:
            with self._database.transaction() as conn:
                conn.execute(
                    text("""INSERT INTO legal_version
                        (id, legal_document_id, version_no, source_id, source_locator,
                         content_sha256, publication_date, effective_from, effective_to,
                         verification_status)
                        VALUES (:id,:document_id,:version_no,:source_id,:source_locator,
                                :content_sha256,:publication_date,:effective_from,:effective_to,'UNVERIFIED')"""),
                    {
                        "id": version.id, "document_id": version.legal_document_id,
                        "version_no": version.version_no, "source_id": version.source_id,
                        "source_locator": version.source_locator, "content_sha256": version.content_sha256,
                        "publication_date": version.publication_date, "effective_from": version.effective_from,
                        "effective_to": version.effective_to,
                    },
                )
                conn.execute(
                    text("""INSERT INTO source_snapshot
                        (id, source_id, legal_version_id, source_url, content_sha256,
                         storage_key, retrieval_status)
                        VALUES (:id,:source_id,:version_id,:source_url,:sha256,:storage_key,'CAPTURED')"""),
                    {
                        "id": snapshot_id, "source_id": version.source_id, "version_id": version.id,
                        "source_url": draft.source_url, "sha256": version.content_sha256,
                        "storage_key": storage_key,
                    },
                )
                for provision in draft.provisions:
                    conn.execute(
                        text("""INSERT INTO legal_provision
                            (id, legal_version_id, locator, heading, text_sha256, content, sequence_no)
                            VALUES (:id,:version_id,:locator,:heading,:text_sha256,:content,:sequence_no)"""),
                        {
                            "id": provision.id, "version_id": provision.legal_version_id,
                            "locator": provision.locator, "heading": provision.heading,
                            "text_sha256": provision.text_sha256, "content": provision.content,
                            "sequence_no": provision.sequence_no,
                        },
                    )
                conn.execute(
                    text("""UPDATE legal_version
                        SET verification_status='VERIFIED'
                        WHERE id=:version_id AND verification_status='UNVERIFIED'"""),
                    {"version_id": version.id},
                )
                if conn.execute(
                    text("SELECT 1 FROM legal_version WHERE id=:id AND verification_status='VERIFIED'"),
                    {"id": version.id},
                ).fetchone() is None:
                    raise RuntimeError("legal version publication failed")
        except Exception:
            self._snapshot_store.delete_if_exists(storage_key)
            raise
        return version.id
