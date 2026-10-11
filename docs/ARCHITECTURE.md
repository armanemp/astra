# Astra Architecture

**Status:** Initial baseline (v0.1)  
**Reviewed:** 2026-10-12

## Style and boundaries

Begin with a modular monolith in one repository. Split into services only when measured load, fault isolation, data residency, or ownership requirements justify the operating cost. Keep stable interfaces across domain rules, application orchestration, model providers, tools, storage, and API adapters.

Trust zones:
1. **Control plane:** API, identity, policy, mission state, approvals, audit, and observability.
2. **Execution plane:** workers/tools with least privilege.
3. **Sandbox plane:** untrusted generated code and artifacts in a restricted runtime.
4. **Release plane:** CI-built artifacts, independent checks, digest-bound approval, staged deploy, and rollback.

An agent cannot weaken policy enforcement, approve its own high-impact change, retrieve secrets by default, or mutate protected main directly.

## Dependency direction

- `domain`: deterministic rules/contracts; no FastAPI, database, model SDK, or infrastructure imports.
- `application`: use cases and orchestration through explicit interfaces.
- `adapters`: model, tool, database, workflow, and storage integrations.
- `api`: validate HTTP requests and invoke application use cases.
- `evaluation`: independently verifies outcomes; planner self-assessment is not sufficient.

## Model gateway and tools

All model providers use one contract. Provider-specific formats stay inside adapters. Each call needs timeout, bounded retries, usage/cost capture, data-handling policy, and structured failure output. Model routing may optimize quality and cost but never grant tool permissions.

Each tool declares ID/version, input/output schema, permission scope, timeout/resource limits, side-effect class, idempotency, and audit metadata. Default policy is deny. Read-only and side-effecting tools use different approval requirements.

## Mission lifecycle and releases

Mission states are a deterministic domain contract. The implementation must pass `VERIFYING` and `AWAITING_APPROVAL` before `RELEASED`. Persistence and workflow execution are introduced in Phase 1, with one authoritative interpretation of domain state. Approval binds to an immutable candidate digest; changed artifacts require re-evaluation and re-approval.

## Data and memory

PostgreSQL is the structured system of record. pgvector is an optional retrieval index, not the source of truth. Large immutable artifacts live in object storage and are addressed by content digest. Memory records include provenance, validity, confidence/review state, and source links.

## Durable workflows

Temporal is the planned runtime for long-running missions, retries, timers, and waits for human approval. Workflow activities should be idempotent; side effects need deduplication or compensation. Keep nondeterministic model/network/tool calls out of deterministic workflow logic.

LangGraph is optional for graph-shaped reasoning flows. It is not mission database, policy engine, or alternative state authority.

## API, UI, and observability

FastAPI provides typed HTTP boundaries. API schemas are versioned under `/api/v1`. Interactive docs are disabled in production by default. The web UI follows after mission APIs exist.

Every request/mission/task/tool call gets correlation IDs. Emit structured logs, traces, usage/cost metrics, policy decisions, and test/artifact references. Redact secrets and minimize sensitive prompt content.

## Hybrid execution

Cloud control plane delegates jobs to registered local/cloud workers. Local bridge uses authenticated outbound communication, scoped workspace access, and revocable identity. Do not create an unauthenticated public inbound endpoint on a local machine.

## Anti-patterns

Competing mission-state owners; parallel tool registries; unbounded retries/cost/recursive delegation; agent self-approval; untraceable vector-only knowledge; microservices before evidence; and release paths that bypass CI.
