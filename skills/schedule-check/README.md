---
summary: For project managers - critical path, float and slip against the approved baseline, computed over the project's working calendar from the schedule tool or SCHEDULE.md, which also keeps the history of baselines.
---

# schedule-check

Checks whether the plan holds. It reads the activities from the project's schedule tool or from `SCHEDULE.md`, runs
a critical path computation over the working calendar of the capacity register, and reports the end date, the
critical path, the float left and how far each date moved from the approved baseline. It keeps `SCHEDULE.md`: the
fallback plan when there is no schedule tool, and the record of every approved baseline whatever tool holds the plan.

## Why

"Are we late?" deserves an answer that does not depend on who reads the Gantt chart. This skill computes dates and
float with a script that knows the project's holidays and closures, measures slip against a named baseline, and ties
moved dates to the approved changes that explain them. A baseline is recorded only with who approved it and when, so
the comparison stays honest.

## Use cases

### Weekly schedule check

**Context:** The plan lives in a schedule file declared in `TOOLS.md`; baseline B-01 was approved at kick-off.

**Action:** Ask "are we late?".

**Result:** The end date against the planned end date and B-01, the critical path, near-critical activities and late
ones, each figure from the script, with the sources it read.

### New baseline after an approved change

**Context:** CR-004 moved the release by two weeks and the steering committee approved the new plan on 2026-11-20.

**Action:** Ask "record the new baseline the committee approved on 20 November".

**Result:** A proposed `B-02` section with the approval date, the approving body, `Change: CR-004` and the planned
dates of each activity; written after you agree; B-01 stays untouched.

### Fallback plan from a spreadsheet

**Context:** The schedule tool only lists dates, with no dependencies.

**Action:** Ask "import the plan into the schedule register".

**Result:** The activities proposed as the register's Activities table, with the dependencies you add, so the
critical path can be computed.

## Usage

Ask in your own words ("critical path", "cammino critico", "slittamento rispetto alla baseline") or run
`/pm-skills:schedule-check`.

## Inputs and outputs

- Reads `PROJECT.md` (declared in `AGENTS.md` or `CLAUDE.md`), the `schedule-check` section of `TAILORING.md`, the
  capacity register (working days), the change log, and the schedule, issues and releases tools listed in
  `TOOLS.md`.
- Writes `SCHEDULE.md` in the format of [`shared/registers/schedule.md`](../../shared/registers/schedule.md), and
  once, with your consent, the `Schedule register` line in `PROJECT.md`.
- Never writes to the schedule tool.
- Takes changes handed off by other skills (for example from meeting minutes), checks them against its own rules, and reports the IDs it assigned.

## Requirements

Python 3 for the shared scripts. A project register (`/pm-skills:project-setup`), and either a schedule tool or a
schedule register. A capacity register (`/pm-skills:capacity-register`) for holidays and closures; without it the
computation uses Monday to Friday.

## Limitations

- Durations are whole working days; dependencies are finish-to-start, start-to-start or finish-to-finish with a lag.
- No resource levelling: activities carry no resources or people.
- A plan read from a tool is only as complete as the tool: missing dependencies are reported, not invented.
