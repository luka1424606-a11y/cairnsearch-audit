# RETRIEVAL AND CITATIONS — v1.1

## 1. Purpose

Сделать retrieval доказательным и контролируемым, а не просто "найти похожий текст".

## 2. Retrieval input

RetrievalRequest:
- authenticated user;
- organization;
- agent;
- query;
- legal date if present;
- document scope;
- conversation context;
- jurisdiction.

## 3. Retrieval stages

1. query normalization;
2. domain detection;
3. date extraction;
4. access scope resolution;
5. exact identifier search;
6. lexical search;
7. semantic search;
8. merge;
9. authority/version/status filters;
10. ranking;
11. evidence sufficiency;
12. evidence packaging.

## 4. Access-first retrieval

ACL must constrain the candidate set before evidence is passed upward.

Do not:
retrieve all
→ filter later in the LLM prompt.

Correct:
authorized scope
→ retrieval.

## 5. Exact search

Preferred for:
- document number;
- article number;
- exact title;
- phrase;
- dates;
- version identifiers.

## 6. Lexical search

Use PostgreSQL full-text search as the primary lexical layer.

The Russian language configuration must be evaluated against the actual Belarusian legal corpus.

Belarusian-language quality must be separately evaluated rather than assumed.

## 7. Semantic search

Embeddings operate on evidence units.

Each embedding must retain:
- evidence ID;
- model identity;
- vector dimension;
- creation time.

Changing embedding models creates a new embedding generation; do not silently overwrite previous model provenance.

## 8. Hybrid merge

All search methods return EvidenceCandidate.

Merge key:
the canonical evidence unit, not just document_id.

Candidate fields:
- evidence_id;
- lexical_score;
- semantic_score;
- authority_score;
- temporal_score;
- final_score.

## 9. Ranking

Ranking can combine:
- lexical relevance;
- semantic relevance;
- source authority;
- temporal validity;
- structure precision.

Weights must be configuration and benchmarked.

Do not assume old cairnsearch 0.3/0.7 weights are correct for legal search.

## 10. Temporal filtering

For legal queries:
- resolve requested date;
- identify candidate versions;
- exclude non-applicable versions before final ranking whenever possible.

If temporal applicability cannot be established, evidence receives an ambiguity state.

## 11. Evidence sufficiency

A candidate set is sufficient only when it passes minimum conditions defined by evaluation.

Thresholds must be derived from test data.

Do not invent universal numeric thresholds.

## 12. Evidence packaging

LLM receives structured evidence:
- evidence ID;
- source type;
- title;
- version;
- provision label;
- effective period;
- source locator;
- text.

The model should not need to infer citation identity from raw filenames.

## 13. Context budget

Context assembly should:
- prioritize directly relevant provisions;
- include neighboring provision context when required for interpretation;
- preserve exceptions and qualifiers;
- avoid unrelated documents;
- avoid duplicate chunks.

## 14. Claim extraction

Generated response is decomposed into claims.

Each material legal claim must be matched to evidence.

## 15. Claim validation statuses

SUPPORTED
PARTIALLY_SUPPORTED
UNSUPPORTED
CONFLICTING
UNVERIFIABLE

Unsupported material claims must not be rendered as supported legal conclusions.

## 16. Citation generation

Citation service produces deterministic citation objects from evidence provenance.

LLM may select evidence IDs from the supplied evidence set but must not author authoritative citation metadata.

## 17. Citation display

For legal evidence, display as much as the source supports:
- document title;
- number;
- date;
- version;
- article/part/item;
- source;
- locator.

Do not display nonexistent fields.

## 18. Internal-document citation

Internal citation must clearly identify:
- internal document;
- version;
- page/section if available.

Never present an internal document as an official legal source.

## 19. Abstention

If no material claim can be sufficiently supported:
status = INSUFFICIENT_EVIDENCE / NOT_CONFIRMED.

Do not fill the gap with model prior knowledge.

A streamed provider response is treated as an internal candidate until validation completes. The final answer is user-visible only after claims, citations and output policy have passed.

## 20. Retrieval evaluation

Required before production:
- Recall@k;
- Precision@k;
- MRR;
- NDCG;
- citation accuracy;
- unsupported claim rate;
- correct abstention rate.

Evaluation corpus must include date-dependent and no-answer questions.

## 21. Deletion consistency

If a document/version/evidence is deleted or revoked:
- retrieval must exclude it;
- embeddings must become invalid;
- citations referencing it must not appear in new answers.

## 22. Provenance

Every evidence item must remain traceable to its original source and version.

No "floating chunk".

