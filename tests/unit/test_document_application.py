from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

from cairnsearch.documents.application import DocumentApplicationService
from cairnsearch.documents.models import Document, DocumentVersion
from cairnsearch.documents.storage import DocumentStorage


def test_create_document_records_audit(tmp_path: Path):
    repo = Mock()
    service = DocumentApplicationService(repo, DocumentStorage(tmp_path))
    org, actor = uuid4(), uuid4()
    document = service.create_document(org, "Политика", "POLICY", actor)
    assert document.organization_id == org
    assert document.created_by == actor
    repo.create_document.assert_called_once_with(document)
    repo.record_audit.assert_called_once_with(document.id, None, actor, "DOCUMENT_CREATED")


def test_add_version_increments_version_and_hashes_content(tmp_path: Path):
    repo = Mock()
    repo.get_latest_version.return_value = DocumentVersion(
        uuid4(), uuid4(), 2, "old", "hash", "text/plain", 3,
        __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )
    service = DocumentApplicationService(repo, DocumentStorage(tmp_path))
    document = Document(uuid4(), uuid4(), "Документ", "POLICY", "ACTIVE", uuid4())
    result = service.add_version(document, b"new content", "text/plain", uuid4())
    assert result.version.version_no == 3
    assert result.version.content_sha256 == DocumentStorage.sha256(b"new content")
    repo.create_version.assert_called_once()
    repo.record_audit.assert_called_once()


def test_empty_document_is_rejected(tmp_path: Path):
    service = DocumentApplicationService(Mock(), DocumentStorage(tmp_path))
    document = Document(uuid4(), uuid4(), "Документ", "POLICY", "ACTIVE", uuid4())
    import pytest
    with pytest.raises(ValueError):
        service.add_version(document, b"", "text/plain", uuid4())
