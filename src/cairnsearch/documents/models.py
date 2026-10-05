"""Domain models for internal documents."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Document:
    id: UUID
    organization_id: UUID
    title: str
    document_type: str
    status: str


@dataclass(frozen=True)
class DocumentVersion:
    id: UUID
    document_id: UUID
    version_no: int
    storage_key: str
    content_sha256: str
    mime_type: str
    byte_size: int
    created_at: datetime


@dataclass(frozen=True)
class DocumentAccess:
    document_id: UUID
    allowed: bool
    reason: str
