# Decisions

## D-001 Background jobs in PostgreSQL

- Date: 2026-03-04
- Status: superseded
- Decided by: Tech lead
- Context: Notifications need retries; the team runs only PostgreSQL today.
- Options: (A) a jobs table in PostgreSQL; (B) a message broker.
- Decision: A jobs table in PostgreSQL, polled by one worker.
- Superseded by: D-002

## D-002 Message broker for notifications

- Date: 2026-09-18
- Status: accepted
- Decided by: steering committee
- Context: Notification volume grew tenfold; the polling worker lags at peak.
- Decision: Move notifications to a managed message broker before the December release.
- Consequences: One more managed service in the budget; the jobs table stays for reports.
- Supersedes: D-001
- Source: `meeting-minutes/2026-09-18-meeting-minutes-steering.md`
