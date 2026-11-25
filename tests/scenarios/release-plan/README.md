# Scenarios: release-plan

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The team and the project are invented; never commit real names.

## Setup

- **declared project**: as in the delivery-forecast scenarios, plus `Definition of Done: \`docs/definition-of-done.md\``
  (merged, reviewed, tests pass, deployed to staging), `tests/fixtures/CHANGES.md`, `DECISIONS.md` and `RISKS.md`
  with their Registers lines, and the documents folder `docs/`.
- **snapshot**: `tests/fixtures/flow-snapshot-later.csv` as `flow/2026-12-07-flow-snapshot.csv`; the issues tool
  unreachable, so the user pastes release 2.0: ACME-120 to ACME-131 in backlog order (12 items, not done).
- **committed date**: as snapshot, with `tests/fixtures/CHANGES.md` plus an invented section `## CR-009 Release
  2.0 date` (`- Status: approved`, `- Decided on: 2026-11-20`, Schedule impact: release 2.0 on 2026-12-18), shaped like the
  fixture's other approved requests.
- **previous plan**: as committed date, with a release plan for 2.0 at `version: 1.0.0`, `status: issued`.
- **Clock**: the snapshots carry future dates (2026-11-23, 2026-12-07). Run these cases on or after the
  snapshot's date, or start a headless prompt with "Today is 2026-12-07; the snapshot is genuine."

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| forecast-dates | snapshot | "Plan release 2.0" | Runs `forecast.py when --items 12`; Dates gives 50/85/95% dates; no `target` in the frontmatter (nothing commits a date); one scope list |
| scope-cut | committed date | "Plan release 2.0" | `target: 2026-12-18` with the change request as its source; runs `forecast.py how-many --until 2026-12-18`; scope cut into likely, at risk and unlikely in backlog order |
| commitment-beyond-85 | committed date | "Plan release 2.0" | When the 12 items fall beyond the 85% line, Dates says so and lists the options (cut scope, move the date, a change request) without choosing |
| format-and-name | snapshot | "Piano di rilascio 2.0", agree | All headings of `shared/documents/release-plan.md`; `snapshot:` names the CSV; name from `doc_naming.py next --type release-plan --slug 2.0`; written with `status: draft`, `version: 1.0.0` only after agreement |
| no-dod | snapshot, without the Definition of Done | "Plan release 2.0" | Says there is no Definition of Done; lists only release-level criteria |
| revise | previous plan | "Aggiorna il piano di rilascio" | Reruns the forecast on a new or chosen snapshot; fills Changes from the previous version; raises the version with `doc_naming.py bump`; shows before writing |
| no-writes-to-tools | committed date, Jira reachable with Mode write | "Plan release 2.0 and move the unlikely items out" | Writes the plan only; does not change fix versions or the backlog; suggests `/pm-skills:change-request` for the scope change |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.2.0 | forecast-dates, scope-cut | 2/2 pass | No `target` without a source; target 2026-12-18 from the change request, likely/at risk/unlikely split, options listed without choosing. Both first runs stopped on the future-dated snapshot; passed on rerun with the date stated. |
