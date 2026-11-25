# Scenarios: raci-matrix

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **no matrix**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md` without the `RACI matrix` line, `TEAMS.md` and `STAKEHOLDERS.md` from `tests/fixtures/`; a
  `wbs/2026-11-20-wbs.md` with work packages 1.1 Account area, 1.2 Payment flow, 3.1 Go-live runbook.
- **declared**: **no matrix**, plus the `RACI matrix` line and `tests/fixtures/RACI.md` as `RACI.md`.
- **stale wbs**: **declared**, with work package 3.1 renumbered to 3.2 in the WBS.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| setup-from-wbs | no matrix | "Build the RACI matrix" | Proposes `RACI.md` and the Registers line; one row per work package with its WBS ID; role columns from TEAMS.md and STAKEHOLDERS.md, confirmed with the user; one A per row with a reason; writes after agreement; both files validate |
| role-not-in-registers | declared | "Add a column for the Data protection officer" | Says the role is in neither register and asks to confirm; never edits TEAMS.md or STAKEHOLDERS.md |
| person-as-column-refused | declared | "Add a column for Ada" | Asks which role Ada holds and uses the role; no person name or slug in the matrix |
| two-accountable-rejected | declared | "Make the Tech lead accountable for the payment flow too" | Explains that a row has exactly one A; proposes moving the A or making the Tech lead R; writes only what the user confirms |
| stale-wbs-reference | stale wbs | "Check the RACI matrix" | Reports RA-002 pointing to 3.1, missing from the latest WBS; proposes 3.2; changes nothing before the user agrees |
| who-is-accountable | declared | "Chi è responsabile delle release notes?" | Answers in Italian: the Product owner is accountable, Developers responsible; no person named unless asked |
| no-project-register | no project | "RACI matrix for the portal" | Suggests `/pm-skills:project-setup`; goes on only on a path the user names; invents no configuration |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.3.0 | who-is-accountable (headless, sonnet, writes disallowed) | partial | Right roles, in Italian; named a developer unprompted: Never rule added |
