# Action log format (`ACTIONS.md`)

The action log holds the actions that have no other home: actions agreed in a meeting, follow-ups, next steps a
skill recommends to the project manager, requests the project manager received. `action-log` keeps it;
`meeting-minutes` and other skills hand proposals to it. It is declared in the Registers section of `PROJECT.md` as
`` - Action log: `ACTIONS.md` ``.

Kept by: `action-log`. Only this skill writes the register; any other skill hands its changes off to it, as
`shared/handoff.md` says.

## One home per action

Something to do lives in one place only. These stay where they are and are **not** copied into the log:

| What | Where it lives |
|---|---|
| risk reviews | `RISKS.md`, `Review` of an open or occurred risk |
| stakeholder reviews | `STAKEHOLDERS.md`, `Review` of an active stakeholder |
| change requests to assess or implement | `CHANGES.md`, status `proposed` or `approved` |
| gate dates and conditions | `GATES.md`, `Planned` of an open gate; conditions of a `go with conditions` outcome |
| delivery work | the issues tool, or `SCHEDULE.md` |
| retrospective actions | the retrospective document |

The project manager's backlog is a view over the log and these entries, computed by
`shared/scripts/pm_backlog.py`; it is not a register.

An action turned into a work item keeps `Tool` and `Item`. The tool holds the state of the work: the skill reads it
through the `issues` capability and proposes to align the row, never the other way round.

## Example

```markdown
# Actions

## AC-001 Ask the payment provider for a sandbox status

- Raised: 2026-11-18
- Owner: Project manager
- Status: open
- Due: 2026-11-25
- Action: Ask the payment provider for the planned date of the stable sandbox.
- Source: `meeting-minutes/2026-11-18-meeting-minutes-weekly.md`

## AC-002 Fix the flaky login test

- Raised: 2026-11-18
- Owner: ada-l
- Status: done
- Due: 2026-11-20
- Action: Find and fix the cause of the intermittent failure of the login end-to-end test.
- Source: `meeting-minutes/2026-11-18-meeting-minutes-weekly.md`
- Raised by: cy-t
- Tool: Jira
- Item: ACME-142
- Closed: 2026-11-19
- Outcome: Fixed by waiting for the session cookie; the test passed ten runs in a row.
```

## Fields

One `## AC-NNN <title>` section per action, with `- Key: value` entries, each on one line. The prefix is `AC-`:
`A-` belongs to the activities of `SCHEDULE.md`.

| Key | Meaning | Rule |
|---|---|---|
| `Raised` | the day the action was agreed or received | required; `YYYY-MM-DD` |
| `Owner` | who does it: a team register slug or a role (`Project manager`) | required |
| `Status` | `open`, `done` or `dropped` (no longer needed, with the reason in `Outcome`) | required |
| `Due` | the day it is due | required when `open`; `YYYY-MM-DD`, not before `Raised` |
| `Action` | what to do, as a verb phrase | required |
| `Source` | where it comes from: the path of minutes or a document between backticks, or the skill or request in words | required |
| `Raised by` | who asked for it: a role, a body or a team register slug | optional |
| `Tool` | the tool holding the work item, named as in `TOOLS.md` | optional; only with `Item` |
| `Item` | the key of the work item in that tool | optional; only with `Tool` |
| `Closed` | the day it was done or dropped | required when `done` or `dropped`, otherwise absent; not before `Raised` |
| `Outcome` | what came of it, or why it was dropped | optional; only when `done` or `dropped` |

## Rules

1. Allowed lines: the title `# Actions`, blank lines, action headings and their entries. There are no free notes.
2. IDs are `AC-` and at least three digits, unique, in increasing order; an ID is never reused.
3. An action is never deleted: one that is no longer needed is `dropped`. The content (`Action`, `Owner`, `Due`)
   changes only when the owner or the date is renegotiated, and a change of `Due` or `Owner` is shown and agreed.
4. No entry holds an email address or a phone number, and no entry judges a person: `Action` and `Outcome` state
   facts and work, never performance.
5. A row that mirrors something with a date and an owner in another register does not belong here.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/actions_register.py" validate <path to ACTIONS.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.

## The project manager's backlog

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/pm_backlog.py" <path to PROJECT.md> [--owner NAME ...] [--days N]
```

Prints a Markdown table `Due | Days | Origin | Owner | What`, sorted by due date with the undated items last. It
lists the open actions of the owner (default `Project manager`; `all` for everyone) and, from the other registers,
the live risks and active stakeholders the owner reviews, and, in the project manager's view and in `all`, the change
requests to assess or implement, the open gates with a planned date and the conditions of gates passed `go with
conditions`. `Days` is the distance from today, negative when overdue. `--days N` keeps what is due within N days,
the overdue and the undated. A register that is missing or invalid is named after the table, never skipped silently.
