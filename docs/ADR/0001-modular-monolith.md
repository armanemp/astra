# ADR-0001: Start with a Modular Monolith

- **Status:** Accepted
- **Date:** 2026-10-12

## Context
Astra is new; premature microservices increase deployment, debugging, security, and compatibility costs before boundaries/load are measured.

## Decision
Start as a modular monolith in one repository with explicit package boundaries and dependency direction. Run isolated workers separately when execution risk or scale requires it. Split services only after a decision supported by observed constraints.

## Consequences
Simpler initial CI/CD, transactions, local development and operations. Package boundaries require discipline; modular contracts keep later separation reversible.
