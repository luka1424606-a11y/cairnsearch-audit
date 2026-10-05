# AGENT SPECIFICATIONS — v1.1

## 1. Common contract

All agents implement the same application contract.

Input:
- user;
- organization;
- agent_code;
- question;
- date_context;
- authorized_scope;
- conversation_context.

Output:
- answer;
- status;
- evidence[];
- citations[];
- warnings[];
- escalation[];
- request_id;
- agent_code;
- model metadata;
- policy_version.

## 2. Common rules

All agents:
- work only with authorized evidence;
- cannot bypass ACL;
- cannot access secrets;
- cannot directly execute SQL/filesystem/network commands;
- cannot invent legal citations;
- must respect jurisdiction policy;
- must return NOT_CONFIRMED when required evidence is absent.

## 3. Legal Agent

Scope:
- legal research;
- contract/document analysis;
- legal risk identification;
- drafting;
- comparison of versions;
- citation-based answers.

Tools:
- legal search;
- internal document search;
- version comparison;
- evidence retrieval;
- citation formatter;
- draft generator.

Forbidden:
- legally binding decisions;
- signature;
- official submission;
- modifying legal source history;
- inventing law or case law.

## 4. HR Agent

Scope:
- employment lifecycle;
- personnel records workflows;
- employment documents;
- internal HR policies;
- analysis against applicable BY legal sources.

Tools:
- authorized internal document search;
- legal evidence retrieval;
- document comparison;
- checklist/draft generation.

Forbidden:
- direct HR record changes without explicit approved application workflow;
- automatic termination decisions;
- unauthorized personnel-data disclosure.

## 5. Occupational Safety Agent

Scope:
- occupational safety requirements;
- instructions;
- training/instruction records;
- internal OSH documents;
- compliance-gap analysis against identified requirements.

Tools:
- legal evidence retrieval;
- internal document search;
- checklist generation;
- comparison;
- draft preparation.

Forbidden:
- automatic certification of full compliance;
- inventing mandatory documents/frequencies;
- overriding safety policy.

## 6. Router

Possible outcomes:
LEGAL
HR
OCCUPATIONAL_SAFETY
MULTI_DOMAIN
UNSUPPORTED

Router can use a deterministic rules layer plus model classification, but final authorization is independent of router choice.

## 7. Multi-domain

A multi-domain question identifies:
- primary agent;
- secondary evidence domains.

Example:
"Can an employee be dismissed for an occupational safety violation?"

Potential domains:
HR + LEGAL + OCCUPATIONAL_SAFETY.

The orchestrator remains bounded:
- maximum steps;
- no unrestricted recursion;
- tool permissions inherited from the active user.

## 8. Agent policy versions

Every agent policy is versioned.

Audit stores:
- policy version;
- model;
- provider;
- request ID.

Production changes create new versions.

Provider/model selection and modification are administrative operations and are not controlled by the LLM.

## 9. Agent memory

No hidden persistent memory of legal facts.

Conversation history is contextual data.

The legal knowledge base is authoritative structured knowledge.

## 10. Output safety

Before output:
- claims validated;
- citations built;
- policy check executed.

If evidence is incomplete:
- downgrade status;
- provide explicit gap;
- escalate where necessary.

## 11. High-risk requests

High-risk categories include:
- termination;
- disciplinary measures;
- safety incidents;
- legal disputes;
- actions affecting rights;
- disclosure of sensitive personnel information.

The agent provides analysis/draft/evidence but does not autonomously execute a legally significant action.

## 12. Human escalation

Escalation payload:
- reason;
- question;
- evidence;
- conflicting sources if any;
- missing information;
- recommended human review point.

## 13. Agent quality tests

Each agent requires:
- domain-routing tests;
- evidence tests;
- unsupported-claim tests;
- ACL tests;
- prompt-injection tests;
- high-risk action refusal tests.

