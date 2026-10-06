from datetime import date
from uuid import uuid4

import pytest

from cairnsearch.legal.models import LegalVersion, VerificationStatus
from cairnsearch.legal.publication_service import LegalPublicationService
from cairnsearch.legal.publishing import ProvisionInput, build_publication_draft


class FakeRepository:
    def __init__(self):
        self.draft = None
        self.source_url = None

    def publish(self, draft, *, source_url):
        self.draft = draft
        self.source_url = source_url
        return draft.version.id


def draft():
    return build_publication_draft(
        legal_document_id=uuid4(), source_id=uuid4(),
        source_url="https://pravo.by/document",
        source_locator="document", version_no=1,
        publication_date=date(2026, 1, 1), effective_from=date(2026, 1, 1),
        effective_to=None, source_content=b"source",
        provisions=[ProvisionInput("статья 1", "Текст", None, 1)],
    )


def test_service_delegates_atomic_publication():
    repo = FakeRepository()
    service = LegalPublicationService(repo)
    value = service.publish(draft(), source_url="https://pravo.by/document")
    assert value == repo.draft.version.id
    assert repo.source_url.endswith("/document")


def test_service_rejects_already_verified_draft():
    d = draft()
    verified = LegalVersion(
        d.version.id, d.version.legal_document_id, d.version.version_no, d.version.source_id,
        d.version.source_locator, d.version.content_sha256, d.version.publication_date,
        d.version.effective_from, d.version.effective_to, VerificationStatus.VERIFIED,
    )
    with pytest.raises(ValueError):
        LegalPublicationService(FakeRepository()).publish(
            type(d)(version=verified, provisions=d.provisions),
            source_url="https://pravo.by/document",
        )
