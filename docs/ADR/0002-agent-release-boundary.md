# ADR-0002: Separate Agent Output from Release Authority

- **Status:** Accepted
- **Date:** 2026-10-12

## Context
A self-improving agent can propose changes to code, prompts, tools and configuration. If it both generates and approves a change, a mistaken or adversarial result could bypass safeguards.

## Decision
Agent-created changes stay in isolated workspaces/branches. Independent CI/evaluation checks the exact artifact. Human approval binds to artifact digest, target, and evaluation/policy versions. Agents cannot modify approval policy or receive production release credentials.

## Consequences
High-impact releases include explicit review. Automation remains useful for research, coding, and testing while release authority stays outside the optimization loop.
