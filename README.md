# Astra

Astra is an evolving, safety-conscious AI assistant platform for research, planning, tool use, durable memory, and evidence-based self-improvement.

> **Status:** Durable mission core in development · **Version:** 0.1.0 · **Production readiness:** Not production-ready

## Implemented baseline

- FastAPI application factory and system endpoints: /api/v1/health/live, /api/v1/health/ready, and /api/v1/meta.
- Typed environment configuration; production requires PostgreSQL and disables interactive API docs.
- Mission create/list/get/transition APIs backed by SQLAlchemy records and Alembic migrations.
- Idempotent creation via the Idempotency-Key header, optimistic concurrency via mission versions, and ordered transition audit history.
- CI quality gates, architecture/security documentation, and a living roadmap.

Authentication, Temporal durable workflows, provider integrations, long-term memory, sandboxed code execution, human approval UI, and production release remain unimplemented. Release and rollback API transitions are deliberately blocked until authenticated approval and a release controller exist.

## Quick start

Requires Python 3.12–3.14 and uv.

1. Install dependencies with uv sync --all-extras.
2. Apply database migrations with uv run alembic upgrade head.
3. Start the API with uv run uvicorn astra.main:app --reload.

For local development the default database is SQLite. Set ASTRA_DATABASE_URL to a PostgreSQL URL for staging/production; production rejects non-PostgreSQL URLs and requires ASTRA_DOCS_ENABLED=false.

## Mission API

- POST /api/v1/missions — requires an Idempotency-Key header (at least 8 characters).
- GET /api/v1/missions?limit=50&offset=0 — bounded pagination.
- GET /api/v1/missions/{id} — current state and ordered audit history.
- POST /api/v1/missions/{id}/transitions — version-checked transition.

Example create request body: {"title":"Investigate a failing test","description":"Reproduce before proposing a patch"}.

## Quality checks

- uv run ruff check .
- uv run mypy src/astra
- uv run pytest --cov=astra --cov-report=term-missing --cov-fail-under=90

See CONTRIBUTING.md, docs/ROADMAP.md, docs/ARCHITECTURE.md, docs/SECURITY.md, and docs/ACCEPTANCE-CRITERIA.md.

## Principles

- One authoritative owner for every state, contract, and policy.
- Small, reversible changes backed by evidence.
- Treat model output and external content as untrusted input.
- Execute generated code only in constrained environments.
- Never let an agent approve its own high-impact release.
- A phase closes only when its acceptance criteria pass.

## License

See LICENSE-DECISION.md. No software license has been selected yet; no open-source license grant should be assumed.
