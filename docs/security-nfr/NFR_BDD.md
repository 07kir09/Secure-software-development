# BDD Scenarios for Security NFRs

```gherkin
Feature: Enforce security non-functional requirements
  The platform must meet security controls before a release is accepted.

  @NFR-S01
  Scenario: Blocking unauthenticated mutation requests
    Given the API is running with authentication enabled
    And a client without a bearer token prepares a POST request to "/items"
    When the client sends the request
    Then the response status code is 401
    And no new item is persisted in the in-memory store

  @NFR-S02
  Scenario: Serving traffic only over TLS 1.2+
    Given the application is deployed behind the reverse proxy
    When a client attempts to call the API over plain HTTP
    Then the proxy responds with a redirect to HTTPS or a 403 status
    And the TLS handshake negotiated uses protocol version TLS 1.2 or newer

  @negative @NFR-S02
  Scenario: Rejecting obsolete TLS clients
    Given a penetration tester forces a TLS 1.0 handshake against the ingress endpoint
    When the handshake negotiation is attempted
    Then the connection is terminated before any HTTP request is processed
    And the security monitor records the downgrade attempt as a high-severity alert

  @NFR-S06
  Scenario: Enforcing 30-day secret rotation
    Given the Secret Manager contains an API token last rotated 25 days ago
    When the scheduled rotation job runs
    Then the job reports the token as compliant
    And the rotation dashboard shows "0" secrets exceeding the 30-day lifetime threshold

  @negative @NFR-S09
  Scenario: Preventing injection payloads in item updates
    Given an authenticated client sends a PUT request with payload "{"name": "<script>alert(1)</script>"}"
    When the request is validated against the ItemUpdate schema
    Then the response status code is 422
    And the application audit log contains an event "rejected_payload" with reason "invalid_characters"
```
