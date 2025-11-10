# ADR-001: Secrets via Environment for API Authorization

Date: 2025-09-22
Status: Accepted

## Context

Mutating endpoints (`POST`/`PUT`/`DELETE /items`) must reject unauthorised callers, yet the prototype ships without an external secret store. Secure Coding guidance from P03 (NFR-S06 / local NFR-05) keeps secrets out of version control, and the Threat Model (flow F2, risk R2) documents how leaked credentials could let internal services abuse the API. We need a deployment-time mechanism that keeps the token out of Git while still supporting local development and CI.

## Decision

FastAPI dependencies for mutating routes read the expected token from the `APP_API_TOKEN` environment variable and compare it to the inbound `X-API-Key` header via `secrets.compare_digest`. Configuration is supplied by Vault or Secret Manager (or a local `.env` file only for development). Missing configuration generates a 500 RFC 7807 problem with a correlation id so gaps surface immediately in CI/CD.

## Consequences

- Pipelines, IaC manifests, and runtime environments must inject `APP_API_TOKEN`; otherwise every write fails fast.
- Test suites rely on a pytest fixture to supply the token, keeping credentials scoped to the current run instead of being hardcoded.
- Operators gain visibility because failed auth attempts now emit RFC 7807 responses with correlation ids. Callers must update their tooling to send the header, but unauthorised access becomes noisy and traceable.

## Links

- NFR-05 / NFR-S06 — Secret rotation and storage (`docs/security-nfr/NFR.md`)
- Threat Model: flow F2 (Reverse Proxy → FastAPI), risk R2 (abuse without mutual auth) (`docs/threat-model/RISKS.md`)
- Test: `tests/test_items.py::test_mutating_without_api_key_returns_401`
