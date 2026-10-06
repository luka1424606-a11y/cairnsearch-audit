"""Temporal legal-version resolver.

Resolution is deterministic and never delegates legal applicability to an LLM.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

from .models import LegalResolution, LegalVersion, ResolutionStatus


def resolve_version(document_id: UUID, as_of: date, versions: list[LegalVersion]) -> LegalResolution:
    candidates = [
        v for v in versions
        if (v.effective_from is None or v.effective_from <= as_of)
        and (v.effective_to is None or as_of <= v.effective_to)
        and v.verification_status.value == "VERIFIED"
    ]
    if len(candidates) == 1:
        return LegalResolution(uuid4(), document_id, as_of, ResolutionStatus.RESOLVED, candidates[0].id, None, __import__("datetime").datetime.now(__import__("datetime").timezone.utc))
    if not candidates:
        return LegalResolution(uuid4(), document_id, as_of, ResolutionStatus.NO_MATCH, None, "No verified version matches date", __import__("datetime").datetime.now(__import__("datetime").timezone.utc))
    return LegalResolution(uuid4(), document_id, as_of, ResolutionStatus.AMBIGUOUS, None, "More than one verified version matches date", __import__("datetime").datetime.now(__import__("datetime").timezone.utc))
