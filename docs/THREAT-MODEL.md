# Initial Threat Model

**Scope:** Foundation and planned agent execution paths. Review before enabling side effects, sandbox execution, or local bridge.

## Assets

Provider credentials; private user files; mission state and memory lineage; source and release artifacts; approval identities/policies; compute budget and worker availability.

## Trust boundaries

User/browser → API; control plane → models; planner → tool registry; worker → sandbox; sandbox → host/network; candidate → verifier; approval → release; cloud → local bridge.

## Threats and mitigations

| Threat | Required mitigation |
|---|---|
| Prompt injection in retrieved content | Treat content as data; deterministic tool policy; adversarial tests |
| Generated code escapes sandbox | Strong isolation, least privilege, quotas, no host socket/broad mounts |
| Agent alters policy or release path | External policy authority, protected branches, separate release credentials |
| Compromised dependency/action | Full-SHA action pins, dependency scans/review, minimal permissions |
| Retry repeats side effect | Idempotency keys, deduplication, compensating action |
| Infinite loop or recursive delegation | Budget, deadline, depth/concurrency caps, circuit breaker, kill switch |
| Poisoned/stale memory | Provenance, validity, review state, deletion and re-evaluation |
| Cross-workspace data access | Explicit scoped permissions and authorization tests |
| Approval replay on changed artifact | Bind approval to digest, target, evaluation and policy version |
| Sensitive prompts in telemetry | Redaction, minimization, retention controls, access restriction |

## Current residual risk

The foundation has no autonomous code runner, durable mission service, or production release engine yet. These threats become implementation gates before those capabilities ship.
