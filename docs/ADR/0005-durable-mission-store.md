# ADR-0005: Durable Mission Store and Optimistic Concurrency

- **Status:** Accepted
- **Date:** 2026-10-12

## Context

Mission state must survive process restarts, duplicate HTTP retries must not create duplicate missions, and concurrent updates must not silently overwrite each other.

## Decision

Use PostgreSQL as the production system of record, SQLAlchemy 2.x for persistence mapping, and Alembic for versioned migrations. The first local-development default is SQLite, while production configuration rejects non-PostgreSQL database URLs. Every mission has a monotonic version; transitions use compare-and-swap semantics and append an event in the same transaction. Mission creation requires an idempotency key tied to a canonical request hash.

Release and rollback are not exposed as operational API actions until authentication, attributable human approval, and a release controller exist. Domain state vocabulary remains separate from persistence and API adapters.

## Consequences

The core can be tested without a running PostgreSQL service, while production deployments use PostgreSQL. Integration tests against PostgreSQL and durable workflow execution remain required before production readiness.
