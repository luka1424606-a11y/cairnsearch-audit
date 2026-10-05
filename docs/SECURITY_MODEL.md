# SECURITY MODEL — целевая система v1.0

## 1. Security objective

Главная цель — исключить:
- несанкционированный доступ к внутренним документам;
- обход ACL через API/LLM;
- утечку секретов;
- destructive startup;
- prompt injection privilege escalation;
- path traversal;
- неподтвержденные юридические ответы;
- потерю юридической истории.

## 2. Security zones

### Zone A — untrusted input
- user prompts;
- uploaded files;
- document text;
- OCR output;
- externally retrieved text.

### Zone B — controlled application
- auth;
- authorization;
- policy;
- retrieval;
- document service.

### Zone C — trusted structured data
- approved legal metadata;
- published legal versions;
- access-control records;
- audit metadata.

### Zone D — secrets
- API keys;
- session secrets;
- encryption keys;
- database credentials.

LLM must never receive secrets.

## 3. Threat model

Threats:
- credential theft;
- broken access control;
- IDOR;
- malicious uploads;
- parser exploitation;
- path traversal;
- prompt injection;
- data exfiltration through tools;
- accidental public exposure;
- stale legal data;
- source tampering;
- unauthorized model/provider switching;
- destructive migrations.

## 4. Authentication

Initial mode:
local accounts + server-side sessions.

Password storage:
- Argon2id or another currently approved adaptive password hash;
- per-user salt handled by the password hashing library;
- parameters documented and benchmarked.

No plaintext passwords.

## 5. Session

Requirements:
- cryptographically random session ID;
- server-side session state;
- expiration;
- logout;
- rotation on privilege changes;
- HttpOnly;
- Secure in HTTPS deployment;
- SameSite;
- no PII in session identifier.

## 6. Authorization

Authorization is mandatory on every protected API path.

Pattern:
authentication
→ role/permission check
→ object-level access check
→ business operation.

UI visibility is not security.

## 7. Default deny

If authorization state is unknown:
DENY.

If ACL resolution fails:
DENY.

If organization scope is unknown:
DENY.

## 8. Object-level authorization

Every access to:
- document;
- document version;
- evidence;
- conversation;
- citation;
- legal administration endpoint

must be checked against the authenticated principal.

Never authorize by sequential ID alone.

## 9. Database defense

Application ACL is primary.

PostgreSQL RLS is an additional defense where practical.

No component may rely on RLS alone to define business permissions.

## 10. LLM boundary

LLM is an untrusted reasoning component.

It does not receive:
- database credentials;
- API keys;
- filesystem root;
- unrestricted shell;
- unrestricted network access.

It only receives authorized context.

## 11. Tool security

Every tool:
- has typed input;
- has explicit permission;
- has risk classification;
- is auditable.

Default for unspecified tool permission:
DENY.

## 12. Prompt injection

Document text is data, never authority.

System instructions, user instructions and retrieved document content must be represented separately.

Injected document text cannot:
- change roles;
- change permissions;
- reveal secrets;
- authorize tools;
- alter policies;
- change provider settings.

## 13. File upload

Requirements:
- allowlist file types;
- validate actual file format;
- size limits;
- generated storage key;
- quarantine;
- parser isolation;
- timeout;
- audit;
- no direct execution.

Never use user-supplied path as a filesystem command.

## 14. Path handling

Forbidden:
- arbitrary open-path endpoint;
- user-controlled shell command;
- path concatenation without canonicalization and allowed-root checking.

Storage references are opaque identifiers, not local filesystem paths.

## 15. Extractor isolation

Where subprocess isolation is supported:
- memory limit;
- CPU timeout;
- process termination;
- stripped environment;
- secrets unavailable;
- no core dumps.

If platform cannot enforce a control, mark it as not implemented rather than claiming isolation.

## 16. Secrets

Secrets must never appear in:
- source;
- Git history;
- frontend code;
- logs;
- audit payloads;
- prompts;
- error messages.

Use environment/secret management appropriate to deployment.

## 17. Network egress

Default policy:
minimum required outbound connectivity.

Local-only mode:
- no cloud LLM traffic;
- no cloud embedding traffic;
- no telemetry.

Any external connection must be explicit and auditable.

## 18. External LLM privacy

When an external provider is used:
- provider and model recorded;
- request metadata audited;
- only minimum evidence sent;
- provider privacy terms reviewed separately.

The application must never claim "no data leaves the machine" when cloud mode is enabled.

## 19. Legal answer safety

A response cannot become "supported" solely because an LLM produced it.

Required:
valid source
+ valid version
+ applicable period
+ authorized access
+ evidence
+ claim validation.

Otherwise:
NOT_CONFIRMED or escalation.

## 20. Audit integrity

Audit:
- append-only for ordinary roles;
- protected admin access;
- no secrets;
- request correlation IDs;
- immutable record identifiers.

Administrative correction, if ever required, must create a new audit event rather than silently rewriting history.

## 21. Error handling

External errors must not reveal:
- filesystem paths;
- credentials;
- SQL statements;
- internal network topology;
- stack traces to ordinary users.

Detailed diagnostics belong in protected logs.

## 22. Security configuration

Security-relevant settings must be:
- explicit;
- validated;
- documented;
- version-controlled when non-secret.

Invalid security configuration must fail closed.

## 23. Security acceptance

Do not call security "complete" until:
- auth tests pass;
- ACL tests pass;
- path traversal tests pass;
- upload tests pass;
- prompt injection tests pass;
- secret leakage tests pass;
- local-only network tests pass;
- backup/restore controls are tested.

