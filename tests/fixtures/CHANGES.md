# Changes

## CR-001 Export of invoices to CSV

- Raised: 2026-09-02
- Requested by: Finance lead
- Status: implemented
- Description: Add a CSV export to the invoice list.
- Reason: Month-end reconciliation is done by hand from screenshots.
- Scope impact: One new endpoint and one button; no change to the data model.
- Schedule impact: none
- Cost impact: 3 person-days within the sprint budget
- Risk impact: none
- Decided by: Product owner
- Decided on: 2026-09-10
- Implemented on: 2026-10-02

## CR-002 Single sign-on with the client directory

- Raised: 2026-10-20
- Requested by: steering committee
- Status: approved
- Description: Replace portal passwords with single sign-on against the client's directory.
- Reason: The client's security policy requires central accounts by the first quarter.
- Scope impact: New login flow; the password reset pages are removed.
- Schedule impact: The December release moves one sprint later.
- Cost impact: 15 person-days, covered by the change budget
- Risk impact: New dependency on the client's directory team.
- Recommendation: Approve, and plan it after the broker migration.
- Decided by: steering committee
- Decided on: 2026-11-04
- Source: `meeting-minutes/2026-11-04-meeting-minutes-steering.md`

## CR-003 Dark mode for the portal

- Raised: 2026-11-12
- Requested by: bo-k
- Status: proposed
- Description: Offer a dark colour scheme in the portal.
- Reason: Asked for by end users in the beta feedback.

## CR-004 Bulk upload of documents

- Raised: 2026-11-16
- Requested by: Support lead
- Status: assessed
- Description: Let users upload up to fifty documents at once.
- Reason: Support uploads month-end batches one file at a time.
- Scope impact: A new upload dialog and a background job.
- Schedule impact: none
- Cost impact: 5 person-days
- Risk impact: none
- Recommendation: Defer to the next release.
