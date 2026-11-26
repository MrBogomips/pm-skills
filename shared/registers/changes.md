# Change log format (`CHANGES.md`)

The change log records every request to change the project's agreed scope, schedule or cost: who asked and why,
its assessed impact, and who decided what. `change-request` keeps it. It is declared in the Registers section of
`PROJECT.md` as `` - Change log: `CHANGES.md` ``.

Kept by: `change-request`. Only this skill writes the register; any other skill hands its changes off to it, as
`shared/handoff.md` says.

## Example

```markdown
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

## CR-002 Replace the portal framework

- Raised: 2026-11-05
- Requested by: bo-k
- Status: rejected
- Description: Rewrite the portal in another framework.
- Reason: No business case stated.
- Recommendation: not assessed
- Decided by: steering committee
- Decided on: 2026-11-05

## CR-003 Dark mode for the portal

- Raised: 2026-11-12
- Requested by: bo-k
- Status: proposed
- Description: Offer a dark colour scheme in the portal.
- Reason: Asked for by end users in the beta feedback.
```

## Fields

One `## CR-NNN <title>` section per change request, with `- Key: value` entries, each on one line.

| Key | Meaning | Rule |
|---|---|---|
| `Raised` | the day the request was recorded | required; `YYYY-MM-DD` |
| `Requested by` | who asked: a role, a body or a team register slug | required |
| `Status` | `proposed`, `assessed`, `approved`, `rejected`, `withdrawn` or `implemented` | required |
| `Description` | the change asked for | required |
| `Reason` | why it is asked | required |
| `Scope impact`, `Schedule impact`, `Cost impact`, `Risk impact` | the assessed impact on each; `none` is a value | required for `assessed`, `approved`, `rejected` and `implemented`, except a `rejected` request with `Recommendation: not assessed`; optional for `proposed` and `withdrawn` |
| `Recommendation` | what the assessor recommends; exactly `not assessed` marks a request rejected at once, without an assessment | optional; `not assessed` only with `rejected` |
| `Decided by` | who decided: a role, a body or a team register slug | required for `approved`, `rejected` and `implemented`; otherwise absent |
| `Decided on` | the day of the decision | as `Decided by`; `YYYY-MM-DD`, not before `Raised` |
| `Decision` | the entry of the decision log that records the decision | optional; one `D-NNN` |
| `Implemented on` | the day the change was delivered | required for `implemented`, otherwise absent; `YYYY-MM-DD`, not before `Decided on` |
| `Source` | where the request came from or was decided: minutes, a ticket, an email thread | optional |

## Rules

1. Allowed lines: the title `# Changes`, blank lines, change request headings and their entries. There are no free
   notes.
2. IDs are `CR-` and at least three digits, unique, in increasing order; an ID is never reused and a request is
   never deleted, whatever its outcome.
3. After a decision only `Status` (to `implemented`), `Implemented on` and corrections of form change; a change of
   mind is a new request.
4. A request may be rejected at once, without an impact assessment, by whoever has the authority to reject it:
   `Status: rejected`, `Recommendation: not assessed`, and `Decided by` and `Decided on` as for any decision.
   Impacts may be left out; a later change of mind is a new request.
5. No entry holds an email address or a phone number, and no entry judges a person.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/changes_register.py" validate <path to CHANGES.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
The validator does not read the decision log: `change-request` checks that a `Decision` exists there.
