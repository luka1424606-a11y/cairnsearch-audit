"""Deterministic citation domain objects and builders."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from uuid import UUID, uuid4

from .models import LegalProvision, LegalVersion, SourceSnapshot, VerificationStatus


@dataclass(frozen=True)
class LegalCitation:
    id: UUID
    legal_version_id: UUID
    provision_id: UUID
    source_snapshot_id: UUID
    citation_key: str
    locator: str
    text_sha256: str
    snapshot_sha256: str


def build_citation(
    *,
    version: LegalVersion,
    provision: LegalProvision,
    snapshot: SourceSnapshot,
) -> LegalCitation:
    if version.verification_status != VerificationStatus.VERIFIED:
        raise ValueError("only VERIFIED legal versions can be cited")
    if version.id != provision.legal_version_id:
        raise ValueError("provision does not belong to legal version")
    if snapshot.legal_version_id != version.id:
        raise ValueError("snapshot does not belong to legal version")
    if provision.text_sha256 != _sha256_text(provision.content):
        raise ValueError("provision content hash mismatch")
    if snapshot.content_sha256 != version.content_sha256:
        raise ValueError("snapshot hash does not match legal version")
    if not provision.locator.strip():
        raise ValueError("provision locator is required")

    key = f"BY:{version.legal_document_id}:v{version.version_no}:{provision.locator}"
    return LegalCitation(
        id=uuid4(),
        legal_version_id=version.id,
        provision_id=provision.id,
        source_snapshot_id=snapshot.id,
        citation_key=key,
        locator=provision.locator,
        text_sha256=provision.text_sha256,
        snapshot_sha256=snapshot.content_sha256,
    )


def format_citation(citation: LegalCitation) -> str:
    """Stable machine-readable citation label for answer generation."""
    return f"[{citation.citation_key} | {citation.locator} | text_sha256={citation.text_sha256}]"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
