# Risks

Scale: 1-5
Last reviewed: 2026-11-20

| ID | Type | Risk | Category | Probability | Impact | Score | Strategy | Response | Owner | Status | Raised | Review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R-001 | threat | If the payment provider's sandbox stays unstable, integration tests slip and the release moves | dependency | 4 | 4 | 16 | mitigate | Contract tests against a local stub; weekly check with the provider | ada-l | open | 2026-10-01 | 2026-12-01 |
| R-002 | threat | If the legacy session module is not refactored, every auth change costs twice the estimate | technical debt | 3 | 3 | 9 | accept | Track the extra effort per sprint | Tech lead | open | 2026-10-15 | 2026-11-15 |
| R-003 | opportunity | If the client approves the shared design system, the web team can reuse its components | scope | 2 | 4 | 8 | enhance | Demo at the next sprint review | bo-k | open | 2026-11-02 | 2026-12-10 |
| R-004 | threat | If the staging environment is not ready by October, load tests cannot start | release | 5 | 3 | 15 |  | Environment ready on 2026-10-20 |  | closed | 2026-09-01 |  |
