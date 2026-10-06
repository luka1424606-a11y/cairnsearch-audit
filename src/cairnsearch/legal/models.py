"""Domain models for Belarus legal knowledge.

The domain deliberately distinguishes a legal document, its immutable version,
its provisions and the official source lineage.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from uuid import UUID


class VerificationStatus(StrEnum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class ResolutionStatus(StrEnum):
    RESOLVED = "RESOLVED"
    NO_MATCH = "NO_MATCH"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class OfficialSource:
    id: UUID
    code: str
    name: str
    base_url: str
    jurisdiction: str
    source_type: str


@dataclass(frozen=True)
class LegalDocument:
    id: UUID
    jurisdiction: str
    document_type: str
    identifier: str
    title: str


@dataclass(frozen=True)
class LegalVersion:
    id: UUID
    legal_document_id: UUID
    version_no: int
    source_id: UUID
    source_locator: str
    content_sha256: str
    publication_date: date | None
    effective_from: date | None
    effective_to: date | None
    verification_status: VerificationStatus


@dataclass(frozen=True)
class LegalProvision:
    id: UUID
    legal_version_id: UUID
    locator: str
    heading: str | None
    text_sha256: str
    content: str
    sequence_no: int


@dataclass(frozen=True)
class SourceSnapshot:
    id: UUID
    source_id: UUID
    legal_version_id: UUID
    source_url: str
    content_sha256: str
    storage_key: str
    retrieval_status: str


@dataclass(frozen=True)
class LegalResolution:
    id: UUID
    legal_document_id: UUID
    as_of_date: date
    status: ResolutionStatus
    legal_version_id: UUID | None
    reason: str | None
    resolved_at: datetime
