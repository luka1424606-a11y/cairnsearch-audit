# DEPLOYMENT — v1.0

## 1. Deployment principle

Deployment is an infrastructure concern, not a business-logic concern.

The same application must support:
- single-machine development;
- private server;
- later controlled cloud deployment.

## 2. Single-machine mode

Components can run on one computer:
- web/API;
- PostgreSQL;
- local file storage;
- optional local LLM.

No domain is required.

Default bind should be local unless the user explicitly configures another interface.

## 3. Private server mode

Reference topology:
- reverse proxy/TLS;
- application;
- PostgreSQL;
- object/local storage;
- background worker;
- optional local/external LLM gateway.

Access can be restricted by network policy.

## 4. Public internet

Not default.

If public exposure is ever enabled:
- HTTPS;
- authentication;
- authorization;
- rate limiting;
- secure headers;
- non-indexing policy;
- no public document endpoints;
- isolated administration.

## 5. Containers

If Docker is used:
- non-root application where practical;
- pinned image versions;
- no unnecessary privileges;
- read-only filesystem where practical;
- secrets injected at runtime;
- explicit network access.

## 6. Database migrations

Use versioned migrations.

Rules:
- forward-only production migrations;
- migration backups for destructive changes;
- schema version recorded;
- startup must never wipe the database.

## 7. Backups

Backup:
- PostgreSQL;
- document storage;
- configuration required for restore;
- key recovery strategy.

Backups must be tested by restoration.

## 8. Restore

Restore sequence must be documented:
1. infrastructure;
2. database;
3. storage;
4. application configuration;
5. keys/secrets;
6. integrity checks;
7. service startup.

## 9. Health

Provide:
- liveness;
- readiness;
- DB connectivity;
- storage accessibility;
- job queue health;
- LLM provider status without leaking credentials.

## 10. Updating

Application update must not:
- delete user files;
- delete legal history;
- reset passwords;
- remove ACL;
- change providers silently.

## 11. Configuration separation

Configuration:
- application config;
- security config;
- provider config;
- storage config;
- legal source config.

Secrets separate from non-secret config.

## 12. External LLM mode

When enabled:
- outbound network route is explicit;
- provider/model are configured;
- usage is logged;
- sensitive context is minimized;
- provider privacy review is required.

## 13. Local-only mode

When enabled:
- external LLM providers are blocked;
- external embeddings are blocked;
- unintended external requests should fail closed.

## 14. No domain dependency

The application must function on:
- localhost;
- private hostname;
- private IP;
without requiring ownership of a public domain.

## 15. Deployment acceptance

A deployment is accepted only after:
- startup;
- login;
- ACL;
- ingestion;
- search;
- agent query;
- citation;
- audit;
- backup;
- restore;
- security checks.

