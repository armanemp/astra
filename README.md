# Astra

Astra is an evolving, safety-conscious AI assistant platform for research, planning, tool use, durable memory, and evidence-based self-improvement.

> **Status:** Foundation bootstrap · **Version:** 0.1.0 · **Production readiness:** Not production-ready

The project is an engineering path toward more capable assistance; it does not claim to implement AGI.

## What exists today

- FastAPI application factory and system endpoints: `/api/v1/health/live`, `/api/v1/health/ready`, and `/api/v1/meta`.
- Typed environment configuration with a fail-safe production policy for interactive API docs.
- Deterministic mission lifecycle contract that prevents skipping verification or approval.
- CI quality gates for supported Python versions.
- Roadmap, architecture, security policy, threat model, acceptance criteria, and ADRs.

Persistence, model integrations, durable workflows, long-term memory, tool execution, sandboxing, approval UI, and production deployment are roadmap items—not implemented features yet.

## Quick start

Requires Python 3.12–3.14 and uv.

```bash
uv sync --all-extras
uv run uvicorn astra.main:app --reload
```

Endpoints:
- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`
- `GET /api/v1/meta`

## Quality checks

```bash
uv run ruff check .
uv run mypy src/astra
uv run pytest --cov=astra --cov-report=term-missing --cov-fail-under=90
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [the roadmap](docs/ROADMAP.md), [architecture](docs/ARCHITECTURE.md), [security](docs/SECURITY.md), and [acceptance criteria](docs/ACCEPTANCE-CRITERIA.md).

## Principles

- One authoritative owner for every state, contract, and policy.
- Small, reversible changes backed by evidence.
- Treat model output and external content as untrusted input.
- Execute generated code only in constrained environments.
- Never let an agent approve its own high-impact release.
- A phase closes only when its acceptance criteria pass.

## License

See [LICENSE-DECISION.md](LICENSE-DECISION.md). No software license has been selected yet; no open-source license grant should be assumed.