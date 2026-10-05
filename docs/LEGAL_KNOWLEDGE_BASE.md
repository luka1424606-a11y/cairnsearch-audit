# LEGAL KNOWLEDGE BASE — Республика Беларусь

## 1. Purpose

Этот слой является каноническим источником нормативных данных для трех агентов.

Основная юрисдикция:
BY.

## 2. Source hierarchy

Knowledge base distinguishes:
1. official legal source;
2. source snapshot;
3. legal document;
4. legal version;
5. legal provision;
6. derived evidence.

Derived text never replaces source provenance.

## 3. Official-source policy

Используются только источники, статус которых подтвержден для системы.

На текущем этапе архитектура ориентируется на официальные государственные правовые ресурсы Республики Беларусь, включая Национальный правовой Интернет-портал и ЭТАЛОН-ONLINE/ресурсы НЦЗПИ.

Для каждого источника отдельно проверяются:
- official status;
- URL stability;
- retrieval mechanism;
- API availability, если заявляется;
- terms/usage restrictions;
- metadata completeness;
- update behavior.

Нельзя считать возможность автоматического скачивания подтвержденной только по наличию сайта.

## 4. Ingestion states

SOURCE_REGISTERED
→ SNAPSHOT_CREATED
→ PARSED
→ STRUCTURED
→ VALIDATED
→ APPROVED
→ PUBLISHED
→ INDEXED

Failure states:
FETCH_FAILED
INTEGRITY_FAILED
PARSING_FAILED
VALIDATION_FAILED
REVIEW_REQUIRED

## 5. Approval gate

Automated parsing may produce a candidate legal version.

Only an approved record can become the published legal knowledge source.

The approval workflow must record:
- reviewer;
- timestamp;
- source snapshot;
- parser version;
- verification status.

## 6. Legal version identity

Version identity cannot be derived only from:
- file name;
- retrieval timestamp;
- latest import order.

Identity should use authoritative metadata and source provenance.

## 7. Effective periods

Every published legal version must have applicability metadata sufficient to evaluate date-dependent questions.

Resolution:
- one confirmed valid version → eligible;
- none → insufficient evidence;
- multiple conflicting candidates → ambiguity.

## 8. Legal hierarchy

Preferred structure:
document
→ version
→ section
→ chapter
→ article
→ part
→ item
→ subitem
→ paragraph.

The parser must preserve the hierarchy when the source provides it.

## 9. Cross-references

Store explicit relations where identifiable:
- amends;
- repeals;
- refers_to;
- related_to;
- revision_of.

Do not infer legal precedence merely from textual similarity.

## 10. Publication and indexing

A published legal version may be marked searchable only when:
- structure is stored;
- provenance is intact;
- required searchable representation exists.

Embedding generation can be asynchronous, but absence of embeddings must be explicit in readiness status.

## 11. Source freshness

The system must expose:
- last retrieved time;
- last verified time;
- last published version;
- source freshness state.

"Fresh" is a system status, not a legal claim.

Exact freshness SLA is a separate operational decision.

## 12. Change detection

Use content hashes and authoritative version identifiers.

When a changed source is detected:
- create new snapshot;
- compare metadata;
- determine whether new legal version exists;
- run validation;
- do not overwrite old snapshot.

## 13. Source conflict

If two official-source snapshots provide apparently conflicting metadata:
- retain both;
- inspect dates/version;
- inspect authority;
- flag conflict;
- do not select randomly.

## 14. Legal document text

The normalized text must preserve meaningful source structure.

Do not normalize away:
- article/item numbering;
- negations;
- exceptions;
- footnotes that affect meaning;
- editorial markers required for provenance.

## 15. Search representation

Maintain both:
- normalized search text;
- source-faithful display text.

Search normalization must not become the only stored legal text.

## 16. Citation requirements

Every legal answer that states a legal rule should be traceable to:
source
→ snapshot
→ legal document
→ legal version
→ provision.

## 17. No-answer states

The knowledge base supports explicit:
- NO_SOURCE;
- NO_VALID_VERSION;
- NO_APPLICABLE_PROVISION;
- CONFLICTING_SOURCE;
- SOURCE_NOT_VERIFIED.

These are first-class states.

## 18. Foreign law

Foreign-law materials are outside the default BY corpus.

Do not silently mix foreign sources with BY legal evidence.

## 19. Legal review boundary

This architecture does not assert that software approval substitutes for legal professional review.

The system can:
- retrieve;
- compare;
- summarize;
- draft;
- flag gaps.

Human responsibility remains for legally significant decisions.

