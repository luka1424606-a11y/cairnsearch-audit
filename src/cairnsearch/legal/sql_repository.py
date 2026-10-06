"""PostgreSQL repository for legal knowledge."""

from __future__ import annotations
from datetime import date
from uuid import UUID
from sqlalchemy import text
from cairnsearch.platform.db import PostgresDatabase
from .models import LegalDocument, LegalProvision, LegalResolution, LegalVersion, ResolutionStatus, VerificationStatus

class PostgresLegalRepository:
    def __init__(self, database: PostgresDatabase):
        self._database = database

    def get_document(self, jurisdiction: str, identifier: str) -> LegalDocument | None:
        with self._database.connection() as conn:
            row = conn.execute(text("""SELECT id, jurisdiction, document_type, identifier, title
                FROM legal_document WHERE jurisdiction=:jurisdiction AND identifier=:identifier"""),
                {"jurisdiction": jurisdiction, "identifier": identifier}).mappings().first()
        if not row: return None
        return LegalDocument(row["id"], row["jurisdiction"], row["document_type"], row["identifier"], row["title"])

    def get_version(self, version_id: UUID) -> LegalVersion | None:
        with self._database.connection() as conn:
            row = conn.execute(text("""SELECT id, legal_document_id, version_no, source_id, source_locator,
                content_sha256, publication_date, effective_from, effective_to, verification_status
                FROM legal_version WHERE id=:version_id"""), {"version_id": version_id}).mappings().first()
        if not row: return None
        return LegalVersion(row["id"], row["legal_document_id"], row["version_no"], row["source_id"],
            row["source_locator"], row["content_sha256"], row["publication_date"], row["effective_from"],
            row["effective_to"], VerificationStatus(row["verification_status"]))

    def get_provision(self, version_id: UUID, locator: str) -> LegalProvision | None:
        with self._database.connection() as conn:
            row = conn.execute(text("""SELECT id, legal_version_id, locator, heading, text_sha256, content, sequence_no
                FROM legal_provision WHERE legal_version_id=:version_id AND locator=:locator"""),
                {"version_id": version_id, "locator": locator}).mappings().first()
        if not row: return None
        return LegalProvision(row["id"], row["legal_version_id"], row["locator"], row["heading"],
            row["text_sha256"], row["content"], row["sequence_no"])

    def list_verified_versions(self, document_id: UUID) -> list[LegalVersion]:
        with self._database.connection() as conn:
            rows = conn.execute(text("""SELECT id, legal_document_id, version_no, source_id, source_locator,
                content_sha256, publication_date, effective_from, effective_to, verification_status
                FROM legal_version WHERE legal_document_id=:document_id AND verification_status='VERIFIED'
                ORDER BY version_no"""), {"document_id": document_id}).mappings().all()
        return [LegalVersion(r["id"], r["legal_document_id"], r["version_no"], r["source_id"], r["source_locator"],
            r["content_sha256"], r["publication_date"], r["effective_from"], r["effective_to"],
            VerificationStatus(r["verification_status"])) for r in rows]

    def save_resolution(self, resolution: LegalResolution) -> None:
        with self._database.transaction() as conn:
            conn.execute(text("""INSERT INTO legal_resolution
                (id, legal_document_id, as_of_date, status, legal_version_id, reason)
                VALUES (:id,:document_id,:as_of_date,:status,:version_id,:reason)
                ON CONFLICT (legal_document_id, as_of_date) DO UPDATE SET
                status=EXCLUDED.status, legal_version_id=EXCLUDED.legal_version_id,
                reason=EXCLUDED.reason, resolved_at=CURRENT_TIMESTAMP"""), {
                "id": resolution.id, "document_id": resolution.legal_document_id,
                "as_of_date": resolution.as_of_date, "status": resolution.status.value,
                "version_id": resolution.legal_version_id, "reason": resolution.reason})

    def get_resolution(self, document_id: UUID, as_of: date) -> LegalResolution | None:
        with self._database.connection() as conn:
            row = conn.execute(text("""SELECT id, legal_document_id, as_of_date, status,
                legal_version_id, reason, resolved_at FROM legal_resolution
                WHERE legal_document_id=:document_id AND as_of_date=:as_of"""),
                {"document_id": document_id, "as_of": as_of}).mappings().first()
        if not row: return None
        return LegalResolution(row["id"], row["legal_document_id"], row["as_of_date"],
            ResolutionStatus(row["status"]), row["legal_version_id"], row["reason"], row["resolved_at"])
