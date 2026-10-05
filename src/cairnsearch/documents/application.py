"""Application services for internal document lifecycle."""

from __future__ import annotations

from dataclasses import dataclass
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
        document = Document(uuid4(), organization_id, title, document_type, "ACTIVE")
        self._repository.create_document(document)
        self._repository.record_audit(document.id, None, actor_user_id, "DOCUMENT_CREATED")
        return document

    def add_version(self, document: Document, content: bytes, mime_type: str,
                    actor_user_id: UUID) -> UploadedVersion:
        previous = self._repository.get_latest_version(document.id)
        next_no = 1 if previous is None else previous.version_no + 1
        storage_key = f"{document.organization_id}/{document.id}/v{next_no}"
        digest = self._storage.sha256(content)
        self._storage.put(storage_key, content)
        version = DocumentVersion(
            uuid4(), document.id, next_no, storage_key, digest,
            mime_type, len(content), __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        )
        self._repository.create_version(version, actor_user_id)
        self._repository.record_audit(document.id, version.id, actor_user_id, "VERSION_CREATED")
        return UploadedVersion(version, storage_key)
