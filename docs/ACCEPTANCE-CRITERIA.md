# Acceptance Criteria and Evaluation Policy

Targets below are initial engineering goals. Calibrate performance targets on reviewed, versioned benchmarks. Safety invariants are hard requirements.

## Hard invariants

- No release without all required checks and current human approval.
- Approval is bound to the exact candidate artifact digest and target.
- No tool runs outside authorized scope or after budget/deadline exhaustion.
- Invalid mission state transitions are rejected deterministically.
- Secrets are never returned by public endpoints or written to application logs.
- Cancellation, timeout, bounded retry, and rollback paths are testable.
- CI and release decisions rely on observed tool/test results, not model assertions.

## Foundation

- CI lint, type check, unit tests, and coverage gate pass on supported Python versions.
- Coverage is at least 90% for current source modules; behavior tests remain mandatory.
- Production config rejects interactive docs unless an explicitly reviewed policy changes it.
- Health endpoints expose no sensitive configuration.
- Clean setup works from documented commands.

## Assistant benchmark (Phase 2)

Record benchmark version, task/input, permitted tools, expected artifact, success rubric, source/evidence requirements, model/provider version, latency, tokens, cost, and tool errors.

Initial targets: >=80% success on a reviewed held-out set of routine tasks; >=95% correct source attribution where external research is required; 100% enforcement of deterministic tool allow/deny cases and configured budgets.

## Self-repair benchmark (Phase 5)

Use versioned faults for syntax/test failures, incorrect assumptions, API/dependency changes, and regression-inducing patches. Measure detection, reproducible failure, repair success, regression, attempts, time, and cost. Initial proposal: solve >=70% of explicitly repairable cases without accepting a patch that fails mandatory regression checks.

## Evaluation integrity

Keep development and held-out data separate. The planner cannot rewrite acceptance criteria for its own run. Save traces, patch digests, test results, evaluator version, and sample counts. Report confidence and per-category regressions rather than overstating small samples.

## Release gate

Release only when required checks are green, critical/high unresolved security findings are zero or explicitly risk-accepted by authorized human, digest matches current approval, health gates pass, and rollback is verified for that deployment class.
