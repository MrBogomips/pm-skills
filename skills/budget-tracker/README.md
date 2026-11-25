---
summary: For project managers - keeps BUDGET.md, the budget lines, reserves, rates per role and approved changes, and tracks spend with earned value and the forecast at completion, every figure from a script.
---

# budget-tracker

Keeps `BUDGET.md`, the project's budget register: budget lines, contingency and management reserve, rates per role
and the approved changes that moved the budget. It gathers actual costs from the costs tool, or hours by role times
the rate in force, and reports earned value: variances, performance indices, estimate at completion and the
reserves left.

## Why

Spend tracked in a spreadsheet nobody reconciles shows up as a surprise at the end. This skill keeps the budget in
one validated file, changes it only through approved change requests or decisions, and computes earned value with a
script so the indices and forecasts can be checked. Costs stay by role and by line: an individual's cost never
enters the file or the report.

## Use cases

### Monthly budget check

**Context:** `TOOLS.md` declares a costs spreadsheet; `BUDGET.md` holds the lines and rates.

**Action:** Ask "where are we on budget at the end of November?".

**Result:** BAC, PV, EV, AC, the variances and indices, EAC, ETC, VAC and TCPI from the script, with the reserves left
reported apart and the sources read.

### Actuals from logged hours

**Context:** There is no costs tool, but the issues tool holds hours logged by role.

**Action:** Ask "compute the actual cost from the logged hours".

**Result:** Hours aggregated by role, each costed at the rate in force with the script, and the total actual cost as
of the status date.

### Record an approved change

**Context:** CR-004 was approved and adds 12,000 EUR to the labor line.

**Action:** Ask "record CR-004 in the budget".

**Result:** A row in Approved changes for the labor line with the signed amount and CR-004, checked against the
change log, written after you agree; the line's original amount stays.

## Usage

Ask in your own words ("earned value", "how much have we spent", "forecast at completion") or run
`/pm-skills:budget-tracker`. Without a budget register the skill starts by setting one up.

## Inputs and outputs

- Reads `PROJECT.md` (declared in `AGENTS.md` or `CLAUDE.md`), the `budget-tracker` section of `TAILORING.md`, the
  team register (roles), the change log, the schedule register, and the costs, issues and schedule tools listed in
  `TOOLS.md`.
- Writes `BUDGET.md` in the format of [`shared/registers/budget.md`](../../shared/registers/budget.md), and once,
  with your consent, the `Budget register` line in `PROJECT.md`.
- Never writes to the costs tool.

## Requirements

Python 3 for the shared scripts. A project register (`/pm-skills:project-setup`). A costs tool is optional: without
it the skill costs logged effort by role, or works from figures you give.

## Limitations

- One currency per project.
- Planned value and percent complete come from a tool or from you; the skill does not estimate progress.
- No individual cost: rates are per role and actuals are aggregated by role or line.
