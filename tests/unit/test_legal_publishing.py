from datetime import date
from uuid import uuid4

import pytest

from cairnsearch.legal.models import VerificationStatus
from cairnsearch.legal.publishing import ProvisionInput, build_publication_draft, sha256_text


def inputs():
    return [
        ProvisionInput("статья 1", "Текст статьи", "Общие положения", 1),
        ProvisionInput("пункт 1", "Первый пункт", None, 2),
    ]


def test_publication_draft_hashes_source_and_provisions():
    draft = build_publication_draft(
        legal_document_id=uuid4(),
        source_id=uuid4(),
        source_url="https://pravo.by/document",
        source_locator="https://pravo.by/document",
        version_no=1,
        publication_date=date(2026, 1, 1),
        effective_from=date(2026, 1, 10),
        effective_to=None,
        source_content=b"official snapshot",
        provisions=inputs(),
    )
    assert draft.version.verification_status == VerificationStatus.UNVERIFIED
    assert len(draft.provisions) == 2
    assert draft.version.content_sha256 == __import__("hashlib").sha256(b"official snapshot").hexdigest()
    assert draft.provisions[0].text_sha256 == sha256_text("Текст статьи")


def test_invalid_source_is_rejected():
    with pytest.raises(ValueError):
        build_publication_draft(
            legal_document_id=uuid4(), source_id=uuid4(),
            source_url="https://example.com/document",
            source_locator="document", version_no=1,
            publication_date=None, effective_from=None, effective_to=None,
            source_content=b"x", provisions=inputs(),
        )


def test_overlapping_date_order_is_rejected():
    with pytest.raises(ValueError):
        build_publication_draft(
            legal_document_id=uuid4(), source_id=uuid4(),
            source_url="https://pravo.by/document",
            source_locator="document", version_no=1,
            publication_date=None, effective_from=date(2027, 1, 1),
            effective_to=date(2026, 1, 1),
            source_content=b"x", provisions=inputs(),
        )


def test_duplicate_locator_is_rejected():
    with pytest.raises(ValueError):
        build_publication_draft(
            legal_document_id=uuid4(), source_id=uuid4(),
            source_url="https://pravo.by/document",
            source_locator="document", version_no=1,
            publication_date=None, effective_from=None, effective_to=None,
            source_content=b"x",
            provisions=[
                ProvisionInput("статья 1", "a", None, 1),
                ProvisionInput("статья 1", "b", None, 2),
            ],
        )
