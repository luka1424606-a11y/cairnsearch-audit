from uuid import uuid4

import pytest

from cairnsearch.legal.citation_service import LegalCitationService
from cairnsearch.legal.models import LegalProvision, LegalVersion, SourceSnapshot, VerificationStatus


class FakeRepository:
    def __init__(self):
        self.saved = None

    def save(self, citation):
        self.saved = citation

    def get_by_key(self, key):
        return None

    def get_for_provision(self, provision_id):
        return self.saved


def make(status=VerificationStatus.VERIFIED):
    document_id, source_id, version_id, provision_id, snapshot_id = [uuid4() for _ in range(5)]
    version = LegalVersion(version_id, document_id, 1, source_id, "source", "a" * 64, None, None, None, status)
    import hashlib
    content = "Норма"
    provision = LegalProvision(provision_id, version_id, "статья 1", None, hashlib.sha256(content.encode()).hexdigest(), content, 1)
    snapshot = SourceSnapshot(snapshot_id, source_id, version_id, "https://pravo.by/document", "a" * 64, "legal/source", "CAPTURED")
    return version, provision, snapshot


def test_service_saves_only_verified_version():
    repo = FakeRepository()
    version, provision, snapshot = make()
    citation = LegalCitationService(repo).create(version=version, provision=provision, snapshot=snapshot)
    assert repo.saved == citation


def test_service_rejects_unverified_version():
    version, provision, snapshot = make(VerificationStatus.UNVERIFIED)
    with pytest.raises(ValueError):
        LegalCitationService(FakeRepository()).create(version=version, provision=provision, snapshot=snapshot)
