# ADR-0004: PostgreSQL as System of Record

- **Status:** Accepted
- **Date:** 2026-10-12

## Context
Astra needs durable mission state, provenance, auditability and semantic retrieval without starting with several unsynchronized stores.

## Decision
Use PostgreSQL for structured state and source metadata. Add pgvector when retrieval benchmarks justify it. Store large immutable artifacts in object storage addressed by content digest. Memory records retain origin, validity, confidence/review state and source links.

## Consequences
A compact initial stack with explicit data ownership. Vector search remains a retrieval index, not a trusted source of facts.
