# ADR-0003: Durable Workflows for Long-Lived Missions

- **Status:** Accepted for Phase 1; implementation deferred
- **Date:** 2026-10-12

## Context
Missions may wait for models, tools, people, services, or local workers. In-memory orchestration loses progress when a process fails.

## Decision
Temporal is the planned runtime for long-lived orchestration, retries, timers and human-approval waits. Keep domain invariants in Astra code, and nondeterministic network/model/tool operations in workflow activities. LangGraph is optional for reasoning graphs, not an alternative mission-state owner.

## Consequences
Recovery is designed in. Temporal adds infrastructure and workflow versioning, so introduce it with restart, cancellation, idempotency and recovery tests rather than as an unused foundation dependency.
