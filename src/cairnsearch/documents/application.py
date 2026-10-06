"""Application services for internal document lifecycle."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .models import Document, DocumentVersion
from .repository import DocumentRepository
from .storage import DocumentStorage


@dataclass(frozen=True)
class UploadedVersion:
    version: DocumentVersion
    storage_key: str


class DocumentApplicationService:
    def __init__(self, repository: DocumentRepository, storage: DocumentStorage):
        self._repository = repository
        self._storage = storage

    def create_document(self, organization_id: UUID, title: str, document_type: str,
                        actor_user_id: UUID) -> Document:
        if not title.strip() or not document_type.strip():
            raise ValueError("title and document_type are required")
        document = Document(uuid4(), organization_id, title.strip(), document_type.strip(), "ACTIVE", actor_user_id)
        self._repository.create_document(document)
        self._repository.record_audit(document.id, None, actor_user_id, "DOCUMENT_CREATED")
        return document

    def add_version(self, document: Document, content: bytes, mime_type: str,
                    actor_user_id: UUID) -> UploadedVersion:
        if not content:
            raise ValueError("content must not be empty")
        previous = self._repository.get_latest_version(document.id)
        next_no = 1 if previous is None else previous.version_no + 1
        storage_key = f"{document.organization_id}/{document.id}/v{next_no}"
        digest = self._storage.sha256(content)
        self._storage.put(storage_key, content)
        version = DocumentVersion(
            uuid4(), document.id, next_no, storage_key, digest,
            mime_type or "application/octet-stream", len(content), datetime.now(timezone.utc),
        )
        try:
            self._repository.create_version(version, actor_user_id)
            self._repository.record_audit(document.id, version.id, actor_user_id, "VERSION_CREATED")
        except Exception:
            self._storage.delete(storage_key)
            raise
        return UploadedVersion(version, storage_key)

    def grant_read(self, document_id: UUID, role_id: UUID, actor_user_id: UUID) -> None:
        self._repository.grant_role_read(document_id, role_id, actor_user_id)

    def revoke_read(self, document_id: UUID, role_id: UUID, actor_user_id: UUID) -> None:
        self._repository.revoke_role_read(document_id, role_id, actor_user_id)
