"""Controlled publication workflow for Belarus legal versions."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

from .models import LegalProvision, LegalVersion, VerificationStatus
from .sources import validate_belarus_source_url


@dataclass(frozen=True)
class ProvisionInput:
    locator: str
    content: str
    heading: str | None
    sequence_no: int


@dataclass(frozen=True)
class PublicationDraft:
    version: LegalVersion
    provisions: tuple[LegalProvision, ...]
    source_content: bytes
    source_url: str


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_publication_draft(
    *,
    legal_document_id: UUID,
    source_id: UUID,
    source_url: str,
    source_locator: str,
    version_no: int,
    publication_date: date | None,
    effective_from: date | None,
    effective_to: date | None,
    source_content: bytes,
    provisions: list[ProvisionInput],
) -> PublicationDraft:
    validate_belarus_source_url(source_url)
    if not source_locator.strip():
        raise ValueError("source_locator is required")
    if not source_content:
        raise ValueError("source_content must not be empty")
    if version_no < 1:
        raise ValueError("version_no must be positive")
    if effective_from and effective_to and effective_from > effective_to:
        raise ValueError("effective_from cannot be after effective_to")
    if not provisions:
        raise ValueError("at least one legal provision is required")

    ordered = sorted(provisions, key=lambda p: p.sequence_no)
    if [p.sequence_no for p in ordered] != list(range(1, len(ordered) + 1)):
        raise ValueError("provision sequence_no must be contiguous starting at 1")

    locators = [p.locator.strip() for p in ordered]
    if any(not locator for locator in locators):
        raise ValueError("provision locator is required")
    if len(locators) != len(set(locators)):
        raise ValueError("provision locators must be unique")

    version = LegalVersion(
        id=uuid4(),
        legal_document_id=legal_document_id,
        version_no=version_no,
        source_id=source_id,
        source_locator=source_locator.strip(),
        content_sha256=hashlib.sha256(source_content).hexdigest(),
        publication_date=publication_date,
        effective_from=effective_from,
        effective_to=effective_to,
        verification_status=VerificationStatus.UNVERIFIED,
    )
    built = tuple(
        LegalProvision(
            id=uuid4(),
            legal_version_id=version.id,
            locator=p.locator.strip(),
            heading=p.heading.strip() if p.heading else None,
            text_sha256=sha256_text(p.content),
            content=p.content,
            sequence_no=p.sequence_no,
        )
        for p in ordered
    )
    return PublicationDraft(
        version=version,
        provisions=built,
        source_content=source_content,
        source_url=source_url,
    )
