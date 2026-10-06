from datetime import date, datetime, timezone
from uuid import uuid4

from cairnsearch.legal.models import LegalVersion, VerificationStatus, ResolutionStatus
from cairnsearch.legal.resolver import resolve_version


def version(no, start, end=None, status=VerificationStatus.VERIFIED):
    return LegalVersion(
        uuid4(), uuid4(), no, uuid4(), "official", "hash",
        date(2025, 1, 1), start, end, status
    )


def test_resolver_returns_resolved_for_one_matching_verified_version():
    document_id = uuid4()
    v = version(1, date(2025, 1, 1))
    result = resolve_version(document_id, date(2026, 1, 1), [v])
    assert result.status == ResolutionStatus.RESOLVED
    assert result.legal_version_id == v.id


def test_resolver_does_not_use_unverified_version():
    document_id = uuid4()
    v = version(1, date(2025, 1, 1), status=VerificationStatus.UNVERIFIED)
    result = resolve_version(document_id, date(2026, 1, 1), [v])
    assert result.status == ResolutionStatus.NO_MATCH


def test_resolver_reports_ambiguous_overlap():
    document_id = uuid4()
    v1 = version(1, date(2025, 1, 1), date(2026, 12, 31))
    v2 = version(2, date(2026, 1, 1))
    result = resolve_version(document_id, date(2026, 6, 1), [v1, v2])
    assert result.status == ResolutionStatus.AMBIGUOUS
