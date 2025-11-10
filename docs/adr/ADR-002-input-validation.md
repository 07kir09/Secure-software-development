# ADR-002: Reject Dangerous Payload Characters

Date: 2025-09-22
Status: Accepted

## Context

Backlog `name` and `description` fields are visible to stakeholders and stored for later processing. Secure Coding backlog items (P03 NFR-S09 / local NFR-03 on RFC 7807 compliance) require sanitising inputs to prevent injection, and the Threat Model (flow F3/F4, risk R3) shows how malformed payloads could tamper with the item store. Previous schemas only enforced length limits, leaving script tags or control characters unfiltered.

## Decision

Pydantic validators on both create and update schemas reject strings containing control characters or angle brackets (`<`, `>`). The guard sits alongside the existing length and status checks, so even partial updates cannot bypass sanitisation. Violations flow through the shared RFC 7807 handler, returning `422 Validation Error` with a correlation id and field-level details.

## Consequences

- Producers embedding HTML-like content must escape or reformat strings. That creates a small DX cost but keeps downstream rendering and storage safe.
- Validation failures surface through consistent problem details, improving troubleshooting even though payload rules are stricter.
- Unit tests cover the rejection path so future schema refactors keep the validator wired in.

## Links

- NFR-03 / NFR-S09 — Input validation and RFC 7807 contract (`docs/security-nfr/NFR.md`)
- Threat Model: flow F3/F4 (FastAPI ↔ Item Store), risk R3 (injection via weak validation) (`docs/threat-model/RISKS.md`)
- Test: `tests/test_items.py::test_create_item_rejects_angle_brackets`
