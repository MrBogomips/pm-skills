# Scenarios: schedule-check

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **no register**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md`, `CAPACITY.md` and `CHANGES.md` from `tests/fixtures/`; no `Schedule register` line and no
  `SCHEDULE.md`.
- **register**: **no register**, plus the line `- Schedule register: \`SCHEDULE.md\`` under Registers and
  `SCHEDULE.md` from `tests/fixtures/` (`Source: register`, ten activities, baselines `B-01` and `B-02` for
  CR-002; Go-live deadline 2027-01-29).
- **tool**: **register** with `Source: Plan` and `TOOLS.md` from `tests/fixtures/` (Plan, Purpose `schedule`, Mode
  `read`); the plan file holds `tests/fixtures/schedule-activities.csv` as a spreadsheet.
- **tool without dependencies**: **tool**, with the Predecessors column emptied in the plan file.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.
- **Registers**: the fixture `PROJECT.md` declares every register; copy the ones a setup names and delete the
  Registers lines of the others, or the hooks report them missing.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| check-register | register | "Are we late? Status as of 2026-11-25" | Runs `schedule_register.py cpm` with `--capacity CAPACITY.md`, `--status-date 2026-11-25`, `--baseline latest`; reports finish 2027-02-16, +22 working days against B-02 (approved 2026-11-04, CR-002), Go-live deadline 2027-01-29 missed (float -12), the three critical paths, Planned end date 2026-12-18 passed; every figure from the script |
| check-tool | tool | "Critical path, please" | Checks Plan is declared with Purpose `schedule`; writes the activities to a temporary CSV outside the project and passes `--activities`; same results as the register |
| tool-no-dependencies | tool without dependencies | "Critical path, please" | Says the tool gave no dependencies and asks for them instead of inventing them; reports no critical path before |
| baseline-approved | register | "Registra la nuova baseline approvata dal comitato di progetto il 2026-11-24" | Proposes `## Baseline B-03 <name>` with Approved 2026-11-24, Approved by the committee, every activity with planned dates from the cpm output; B-01 and B-02 untouched; writes after agreement; validates |
| baseline-unapproved-cr | register | "Record the new baseline approved by the steering committee today for CR-004" | Says CR-004 is only assessed in the change log; does not cite it as `Change` until it is approved; asks how to proceed |
| baseline-no-approver | register | "Save the current plan as the new baseline" | Asks who approved it and when; records nothing until the user says |
| baseline-edit-refused | register | "Change B-02's finish date for A-007" | Refuses to edit a recorded baseline; offers a new baseline after approval |
| update-progress | register | "A-007 started on 2026-11-23 and is 20% done" | Shows the row change, writes after agreement, validates |
| import-fallback | tool, with no `## Activities` in `SCHEDULE.md` | "Import the plan into the schedule register" | Proposes the Activities table from the tool; no person or resource column; keeps `Source: Plan` unless the user makes the register the source; writes after agreement; validates |
| cycle | register with A-001 depending on A-003 and A-003 on A-001 | "Check the schedule" | Shows the script's cycle error; proposes the fix; reports no dates |
| setup | no register | "Set up the schedule register" | Proposes `SCHEDULE.md` with `Source: register`, an Activities table built with the user and the Registers line; validates both files |
| no-project-register | no project | "Are we late?" | Suggests `/pm-skills:project-setup`; invents no configuration |
| handoff-accepted | register | A handoff proposal: record a new baseline approved by the steering committee on 2026-11-20 | Asks for anything missing (who approved, when), shows, writes on agreement, validates and reports the baseline |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.2.0 | check-register, baseline-edit-refused, baseline-unapproved-cr | 3/3 pass | Finish 2027-02-16, +22 days, deadline missed (float -12); B-02 refused edit; CR-004 not cited, nothing written. |
