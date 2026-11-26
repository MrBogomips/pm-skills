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
| person-as-column-refused | declared | "Add a column for Ada to the RACI matrix" | Asks which role Ada holds and uses the role; no person name or slug in the matrix |
| two-accountable-rejected | declared | "Make the Tech lead accountable for the payment flow too" | Explains that a row has exactly one A; proposes moving the A or making the Tech lead R; writes only what the user confirms |
| stale-wbs-reference | stale wbs | "Check the RACI matrix" | Reports RA-002 pointing to 3.1, missing from the latest WBS; proposes 3.2; changes nothing before the user agrees |
| who-is-accountable | declared | "Chi è responsabile delle release notes?" | Answers in Italian: the Product owner is accountable, Developers responsible; no person named unless asked |
| no-project-register | no project | "RACI matrix for the portal" | Suggests `/pm-skills:project-setup`; goes on only on a path the user names; invents no configuration |
| handoff-accepted | declared | A handoff proposal: add a row for work package 3.2 with Tech lead accountable | Checks one accountable role per row, computes the RA- ID, shows, writes on agreement, validates and reports the ID |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.3.0 | who-is-accountable (headless, sonnet, writes disallowed) | partial | Right roles, in Italian; named a developer unprompted: Never rule added |
| 2026-11-25 | 1.3.1 | setup-from-wbs, role-not-in-registers, person-as-column-refused, two-accountable-rejected, stale-wbs-reference, who-is-accountable (re-run), no-project-register (headless, writes disallowed) | setup-from-wbs pass; role-not-in-registers pass; person-as-column-refused partial; two-accountable-rejected pass; stale-wbs-reference pass; who-is-accountable pass; no-project-register pass | person-as-column-refused: did not ask which role Ada holds; offered an option to add an 'Ada L.' column (person name in the matrix) next to the role columns, wrote nothing. who-is-accountable: Italian, roles only, and offered the names only on request (the earlier gap is closed) |
| 2026-11-25 | 1.3.1 | person-as-column-refused (re-run after fixes, headless, writes disallowed) | partial | No person column offered any more and nothing written, but it did not ask which role Ada holds; asked 'which file or table do you mean' instead |
| 2026-11-25 | 1.3.1 | person-as-column-refused, prompt naming the RACI matrix (headless, writes disallowed) | pass | Wrote nothing; offered no person column; asked which role to use (Developers already a column, Reviewer missing) with empty letters until the user decides |
