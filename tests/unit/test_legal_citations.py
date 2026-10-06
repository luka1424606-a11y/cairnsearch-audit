from uuid import uuid4

import pytest

from cairnsearch.legal.citations import build_citation
from cairnsearch.legal.models import LegalProvision, LegalVersion, SourceSnapshot, VerificationStatus


def objects():
    document_id, source_id, version_id, provision_id, snapshot_id = [uuid4() for _ in range(5)]
    version = LegalVersion(
        version_id, document_id, 3, source_id, "source",
        "a" * 64, None, None, None, VerificationStatus.VERIFIED,
    )
    provision = LegalProvision(
        provision_id, version_id, "статья 12, пункт 2", None,
        __import__("hashlib").sha256("Правило".encode()).hexdigest(),
        "Правило", 1,
    )
    snapshot = SourceSnapshot(
        snapshot_id, source_id, version_id, "https://pravo.by/document",
        "a" * 64, "legal/source", "CAPTURED",
    )
    return version, provision, snapshot


def test_citation_is_deterministic_and_bound_to_hashes():
    version, provision, snapshot = objects()
    citation = build_citation(version=version, provision=provision, snapshot=snapshot)
    assert citation.citation_key.startswith("BY:")
    assert citation.locator == "статья 12, пункт 2"
    assert citation.text_sha256 == provision.text_sha256
    assert citation.snapshot_sha256 == snapshot.content_sha256


def test_wrong_snapshot_is_rejected():
    version, provision, snapshot = objects()
    bad = SourceSnapshot(
        snapshot.id, snapshot.source_id, snapshot.legal_version_id,
        snapshot.source_url, "b" * 64, snapshot.storage_key, snapshot.retrieval_status,
    )
    with pytest.raises(ValueError):
        build_citation(version=version, provision=provision, snapshot=bad)
