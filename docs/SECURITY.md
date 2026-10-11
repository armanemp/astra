# Security Policy and Mandatory Boundaries

Astra will execute model-generated plans and eventually generated code. User input, retrieved pages, files, tool outputs, model responses, repositories, and memory records are untrusted data.

## Mandatory controls

- Default-deny tool authorization and least-privilege credentials.
- Separate control, worker, sandbox, and release trust zones.
- No secrets in prompts, fixtures, logs, repo files, or sandbox environments.
- No direct agent write/merge/deploy permission to protected main.
- Human approval for high-impact release; bind it to artifact digest, target, evaluation, and policy version.
- Bound token/cost, runtime, concurrency, retries, filesystem, CPU, memory, and network.
- Reliable cancellation and global stop mechanism.
- Audit permission decisions, tool use, approvals, releases, and rollbacks.
- Pin GitHub Actions to full commit SHAs, scan dependencies, and minimize CI token permissions.
- Never expose secrets through errors or telemetry.

## Sandbox

A container helps but is not a complete boundary. Avoid privileged/root execution where possible, Docker socket mounts, broad host paths, and provider credentials. Apply CPU/memory/PID/time limits, temporary workspaces, explicit egress policy or disabled networking, runtime restrictions, and cleanup. Evaluate gVisor or microVM isolation for higher-risk code.

## Prompt injection and tools

Retrieved content may contain hostile instructions. Keep policy outside retrieved content, validate each tool call deterministically, and require confirmation for sensitive side effects. A model's explanation is not proof that an operation is safe.

## Secrets and data

Use a cloud secrets manager and a platform-appropriate local secret store. Never log secret values. External-provider data transfer must follow explicit provider, retention, region, and sensitivity policy. Define minimization, retention, and deletion before production.

## Approval and incident response

Evaluate the exact release candidate; store its digest; record approver, timestamp, environment, and policy/evaluation versions. Reject changed or stale approvals. Use staged rollout and test rollback. Security-policy or permission changes require elevated human review.

Incident procedure must support pausing missions, revoking credentials, isolating workers, preserving audit evidence, rollback, and documenting recovery. This project is not production-ready until an explicit reporting and response process is configured.
