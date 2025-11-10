# ADR-003: Standardise API Errors with RFC 7807

Date: 2025-09-22
Status: Accepted

## Context

Earlier responses wrapped errors in bespoke `{"error": ...}` bodies with inconsistent fields and no correlation identifier. Secure Coding guidance (P03 NFR-03) calls for predictable failure payloads, and the Threat Model (flow F1, risk R5) warns that leaking raw exceptions hinders monitoring and expands the attack surface. We need a standards-based error surface that clients and observability tooling can trust.

## Decision

Introduce a reusable RFC 7807 helper that emits `application/problem+json` responses. The helper generates UUID v4 correlation ids, sets `type`, `title`, `status`, and `detail`, and accepts optional diagnostics such as field-level error lists. All custom exceptions (`ApiError`, validation handlers, FastAPI `HTTPException`) now route through this helper.

## Consequences

- Client integrations must parse RFC 7807 fields. Legacy parsing may break until updated, but interoperability improves afterwards.
- The correlation id is copied to both the response body and `X-Correlation-ID` header, simplifying log stitching with minimal overhead.
- Error catalogue maintenance becomes disciplined because codes map to canonical problem URIs, and developers receive clearer diagnostics.

## Links

- NFR-03 — RFC 7807 compliant errors (`docs/security-nfr/NFR.md`)
- Threat Model: flow F1 (Product Manager → Reverse Proxy), risk R5 (API response leakage) (`docs/threat-model/RISKS.md`)
- Test: `tests/test_errors.py::test_rfc7807_contract`
