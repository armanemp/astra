# Contributing to Astra

Astra is in foundation and durable-core development. Keep changes small, reversible, tested, and consistent with docs/ADR/.

## Prerequisites and setup

Install Python 3.12–3.14 and uv.

- uv sync --locked --all-extras
- uv run alembic upgrade head
- uv run pytest
- uv run ruff check .
- uv run mypy src/astra

When changing dependencies, update pyproject.toml and uv.lock together using uv lock. Review the lockfile diff and verify uv sync --locked --all-extras before opening a PR. CI must not silently regenerate the lockfile.

Do not commit virtual environments, local databases, .env files, credentials, or private data.

## Change process

1. Reference an issue or write observable acceptance criteria.
2. Create a focused branch; do not bundle unrelated refactors.
3. Add or update tests for behavior changes.
4. Update docs and the relevant ADR when a decision changes.
5. Run lint, type checks, tests, and relevant security checks.
6. Open a PR with context, test evidence, risks, and rollback notes.
7. CI and required human review—not the agent's self-assessment—determine correctness.

## Engineering rules

- Keep domain logic independent of web frameworks, model SDKs, and infrastructure.
- Validate all external input at boundaries.
- Treat prompts, model responses, retrieved documents, and generated code as untrusted.
- Prefer explicit contracts and deterministic tests.
- New dependencies require a reason and compatibility review.
- Every autonomous loop needs time/cost budgets, retry ceilings, cancellation, and a stop condition.
- Agents must not push directly to protected main or approve their own high-impact changes.
