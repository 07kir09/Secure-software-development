# NFR Traceability Matrix

| NFR ID  | Story / Task ID | Story / Task Title                                              | Issue / Milestone Link*                                                                                   | Release Window          | Priority |
|---------|-----------------|-----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|-------------------------|----------|
| NFR-S01 | STORY-SEC-01    | Enforce bearer-token auth for mutating endpoints                | Planned GitHub issue (`story-sec-01`) to be opened under Milestone `MVP-Security`                         | Sprint 3 (MVP-Security) | P0       |
| NFR-S02 | TASK-SEC-08     | Configure TLS 1.2+ termination at ingress                       | Planned GitHub issue (`task-sec-08`) tracked in Milestone `Hardening-Alpha`                               | Sprint 4 (Hardening)    | P1       |
| NFR-S03 | STORY-SEC-05    | Implement structured audit logging for item mutations           | Planned GitHub issue (`story-sec-05`) in Milestone `Audit-Enablement`                                     | Sprint 4 (Hardening)    | P1       |
| NFR-S04 | TASK-SEC-02     | Add dependency vulnerability scanning and CI gate               | GitHub issue [`#15`](https://github.com/kirillvoyakin/course-project-07kir09/issues/15) *(to be created)* | Sprint 2 (CI-Enable)    | P0       |
| NFR-S05 | TASK-SEC-11     | Introduce rate limiting middleware in reverse proxy             | Planned GitHub issue (`task-sec-11`) under Milestone `Hardening-Beta`                                    | Sprint 5 (Stabilize)    | P2       |
| NFR-S06 | TASK-SEC-03     | Centralize secret storage and automate 30-day rotation          | Planned GitHub issue (`task-sec-03`) in Milestone `Secrets-Hardening`                                     | Sprint 2 (CI-Enable)    | P0       |
| NFR-S07 | TASK-SEC-09     | Enforce security response headers via middleware                | Planned GitHub issue (`task-sec-09`) under Milestone `Hardening-Beta`                                    | Sprint 4 (Hardening)    | P1       |
| NFR-S08 | STORY-SEC-07    | Encrypt and test restore of backups                             | Planned GitHub issue (`story-sec-07`) in Milestone `Resilience-Release`                                   | Sprint 6 (Resilience)   | P2       |
| NFR-S09 | STORY-SEC-04    | Strengthen input validation and injection defenses              | Planned GitHub issue (`story-sec-04`) linked to Milestone `MVP-Security`                                  | Sprint 3 (MVP-Security) | P0       |

\*Если фактический номер issue ещё не создан, указано planned обозначение; обновите ссылку после создания задачи.
