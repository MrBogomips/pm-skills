# Decision log format (`DECISIONS.md`)

The decision log records the decisions that shape the project, with their context, the options considered and who
took them, so that later work can rely on them and later readers know why. `decision-log` keeps it;
`meeting-minutes` proposes entries for it. It is declared in the Registers section of `PROJECT.md` as
`` - Decision log: `DECISIONS.md` ``.

## Example

```markdown
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
```

## Fields

One `## D-NNN <title>` section per decision, with `- Key: value` entries, each on one line.

| Key | Meaning | Rule |
|---|---|---|
| `Date` | the day the decision was taken | required; `YYYY-MM-DD` |
| `Status` | `accepted` (in force), `superseded` (replaced by a later decision) or `revoked` (withdrawn with nothing in its place) | required |
| `Decided by` | who took it: a role, a body (steering committee) or a team register slug | required |
| `Context` | the problem and the constraints that forced a decision | required |
| `Decision` | what was decided | required |
| `Options` | the options considered, the chosen one included | optional |
| `Consequences` | what follows: costs, risks, work, what it rules out | optional |
| `Supersedes` | the decision this one replaces | optional; one `D-NNN` |
| `Superseded by` | the decision that replaced this one | required when `superseded`, otherwise absent |
| `Source` | where the decision was taken or recorded: minutes, an email thread, a ticket | optional |

## Rules

1. Allowed lines: the title `# Decisions`, blank lines, decision headings and their entries. There are no free
   notes.
2. IDs are `D-` and at least three digits, unique, in increasing order; an ID is never reused.
3. A decision is never deleted or rewritten after it is accepted: a change of mind is a new decision that
   supersedes it. Only its `Status` and `Superseded by` change, and corrections of form (a typo, a moved `Source`
   path) that leave the meaning intact. `Supersedes` and `Superseded by` always point to each other.
4. No entry holds an email address or a phone number, and no entry judges a person.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/decisions_register.py" validate <path to DECISIONS.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
