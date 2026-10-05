# TEST STRATEGY — v1.0

## 1. Principle

A visible UI control is not proof of functionality.

Every required function must be executable and testable.

## 2. Unit tests

Cover:
- domain entities;
- legal version resolution;
- effective periods;
- ACL;
- permission checks;
- citation construction;
- claim validation;
- policy evaluation;
- deterministic identifiers;
- idempotency.

## 3. Integration tests

Use a disposable PostgreSQL test database.

Test:
- migrations;
- legal ingestion;
- document ingestion;
- pgvector;
- lexical search;
- hybrid search;
- auth;
- sessions;
- ACL;
- audit;
- LLM Gateway adapters.

## 4. API tests

For every protected endpoint:
- authenticated happy path;
- unauthenticated;
- wrong role;
- wrong object ownership;
- revoked access;
- malformed request.

## 5. Security tests

Mandatory:
- IDOR;
- privilege escalation;
- path traversal;
- unsafe upload;
- parser timeout;
- malicious document;
- prompt injection;
- secret leakage;
- CSRF where cookie auth is used;
- session fixation;
- session reuse after privilege change;
- CORS misconfiguration;
- local-only network leakage.

## 6. Legal data tests

Test:
- multiple versions;
- effective periods;
- status;
- source snapshots;
- content hash mismatch;
- parser failure;
- approval gate;
- source conflict;
- missing source;
- missing provision.

## 7. Retrieval tests

Dataset columns:
- question;
- date;
- expected source;
- expected version;
- expected provision;
- expected rank;
- no-answer flag.

Metrics:
- Recall@k;
- Precision@k;
- MRR;
- NDCG.

## 8. Citation tests

For every expected answer:
- citation exists;
- citation points to real evidence;
- evidence points to correct source;
- version is correct;
- locator is correct where available.

## 9. Claim validation tests

Include:
- supported claim;
- partially supported claim;
- unsupported claim;
- conflicting evidence;
- missing version;
- stale evidence.

Expected behavior is machine-checked.

## 10. Agent tests

Each agent gets:
- routing tests;
- domain leakage tests;
- tool permission tests;
- high-risk refusal tests;
- citation tests;
- unsupported-answer tests.

## 11. Negative acceptance suite

NEG-01 no auth → deny.
NEG-02 foreign internal document → deny.
NEG-03 no legal evidence → NOT_CONFIRMED.
NEG-04 ambiguous versions → ambiguity/not confirmed.
NEG-05 prompt injection in document → treated as data.
NEG-06 path traversal → deny.
NEG-07 startup → no data deletion.
NEG-08 invalid citation → claim rejected.
NEG-09 revoked access → excluded.
NEG-10 forbidden legal action → deny/escalate.
NEG-11 cloud provider in local-only mode → no outbound call.
NEG-12 source hash mismatch → no publication.
NEG-13 duplicate ingestion → no duplicate version.
NEG-14 deleted internal document → no new retrieval result.
NEG-15 downgraded role → new access rights apply.

## 12. Data-integrity tests

Verify:
- no orphan embeddings;
- no orphan citations;
- no orphan provisions;
- no broken legal version lineage;
- no broken ACL references;
- transactional consistency after failures.

## 13. Migration tests

Every schema migration is tested:
- clean install;
- previous supported version;
- interrupted migration recovery;
- rollback strategy where supported.

## 14. Performance tests

Measure:
- p50/p95 retrieval latency;
- ingestion throughput;
- OCR duration;
- API latency;
- database query time;
- vector search latency.

Do not optimize for latency at the cost of evidence correctness.

## 15. Recovery tests

Verify:
- database restore;
- document restore;
- configuration restore;
- key recovery;
- application restart after restore.

## 16. Definition of done

A feature is done only if:
- implementation exists;
- automated test exists where appropriate;
- negative behavior is tested;
- authorization is tested;
- logs/audit are correct;
- documentation reflects reality.

