# Astra Roadmap

**Status:** Living plan — foundation bootstrap  
**Last reviewed:** 2026-10-12  
**Owner:** Repository maintainers

This roadmap changes only when decisions and evidence are documented. A phase is complete only when acceptance criteria pass; elapsed time never closes a phase. This is an engineering roadmap, not a claim that Astra is AGI.

## Product direction

Build a general-purpose assistant that can research, plan, use constrained tools, retain attributable memory, evaluate outcomes, and improve its own software through reversible, evidence-based cycles. Humans keep control of production releases and high-impact safety-policy changes.

## Operating principles

1. One authoritative owner per state, contract, and policy.
2. Build the smallest complete, testable capability before adding parallel subsystems.
3. Separate model judgment from deterministic enforcement and independent verification.
4. Treat input and output from users, tools, websites, files, and models as untrusted.
5. Keep lineage, evaluation artifacts, dependency versions, and decisions traceable.
6. Every autonomous loop has a budget, deadline, retry ceiling, cancellation path, and stop condition.
7. Production releases require independent checks and attributable human approval.

## Phases and gates

### Phase 0 — Engineering foundation (in progress)
Deliverables: repository conventions, typed settings, FastAPI factory, health/metadata endpoints, mission lifecycle contract, tests, CI, ADRs, security policy, threat model, and acceptance scorecard.

Exit criteria: CI passes on all supported Python versions; invalid mission transitions are rejected; production config disables interactive docs; setup is documented; no secrets or unbounded execution paths are introduced.

### Phase 1 — Durable mission core
Deliverables: PostgreSQL schema/migrations, repository interfaces, mission/task APIs, idempotency keys, transactional state transitions, Temporal workflows, and restart/retry tests.

Exit criteria: state survives process restarts; duplicate requests do not duplicate effects; retry/cancellation/timeouts are deterministic and observable.

### Phase 2 — Model gateway and useful assistant
Deliverables: provider-neutral model contract, adapters, structured outputs, timeouts/retry rules, token/cost metering, research/file tools, planner, and evidence-aware responses.

Exit criteria: provider failures and malformed output fail safely; budgets are enforced; tool calls are validated and audited; a versioned benchmark measures success and groundedness.

### Phase 3 — Durable memory and retrieval
Deliverables: context management, attributable knowledge records, PostgreSQL search and pgvector where justified, ingestion, retention/deletion policy, and memory-quality evaluation.

Exit criteria: facts retain sources, timestamps, confidence, and review state; unverified claims are not promoted silently; retrieval and deletion tests pass.

### Phase 4 — Sandboxed development tools
Deliverables: isolated runner, scoped files, resource/network limits, generated patches, test execution, artifact hashes, and cleanup.

Exit criteria: host secrets/files stay inaccessible by default; resource ceilings work; artifacts/reports are attributable; malicious tool output and prompt injection are covered by security tests.

### Phase 5 — Self-repair
Deliverables: failure triage, reproduction tests, patch proposal, independent evaluation, bounded repair attempts, and rollback.

Exit criteria: fault benchmarks meet an agreed success target; regression-causing patches are rejected; loop termination, budget limits, cancellation, and rollback are tested; agents cannot self-approve or push to main.

### Phase 6 — Human approvals and release engineering
Deliverables: approval UI, immutable approval bound to artifact digest, protected release workflow, staged rollout, health gates, and rollback drills.

Exit criteria: changed artifacts invalidate approvals; no release occurs without approval and required checks; rollback is verified.

### Phase 7 — Hybrid local/cloud execution
Deliverables: local bridge, authenticated outbound connection, worker identity, explicit workspace scopes, reconnect behavior, local-model option, and worker lifecycle.

Exit criteria: no public inbound endpoint is required for local work; local permissions are scoped/revocable; interrupted work resumes or stops per policy; sensitive content is not sent without authorization.

### Phase 8 — Evidence-based capability growth
Deliverables: model-routing experiments, prompt/workflow optimization, tool-generation proposal pipeline, optional fine-tuning experiments, and cross-version benchmark reports.

Exit criteria: improvements beat a versioned baseline on held-out tasks; regressions/cost/latency/uncertainty are reported; experimental learning cannot bypass release rules or change its own controls.

## Definition of done

Every change has a problem/acceptance criterion, focused implementation, tests, security impact review, relevant docs, reproducible CI evidence, review, and rollback strategy for operational changes.

## Current next actions

1. Finish foundation bootstrap after CI passes on the supported matrix.
2. Add persisted mission records and migrations as one atomic work package.
3. Introduce durable execution with restart/retry/cancellation acceptance tests.
4. Do not enable autonomous tool actions until deterministic contracts and budgets exist.
