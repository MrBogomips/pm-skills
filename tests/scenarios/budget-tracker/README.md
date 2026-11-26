# Scenarios: budget-tracker

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **no register**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md`, `TEAMS.md` and `CHANGES.md` from `tests/fixtures/`; no `Budget register` line and no `BUDGET.md`.
- **register**: **no register**, plus the line `- Budget register: \`BUDGET.md\`` under Registers and `BUDGET.md`
  from `tests/fixtures/` (labor B-001, expenses B-002 and B-003, contingency B-004, management reserve B-005; rates
  per role; approved changes for D-002 and CR-002), and `DECISIONS.md` from `tests/fixtures/`.
- **with costs**: **register**, plus `TOOLS.md` from `tests/fixtures/` (Plan, Purpose `schedule, costs`, Mode
  `read`), the plan file holding actuals and planned value by month.
- **with hours**: **register**, plus a `TOOLS.md` with a `file:` issues export of hours logged, with an assignee
  column, declared with Purpose `issues`, Mode `read`.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.
- **Registers**: the fixture `PROJECT.md` declares every register; copy the ones a setup names and delete the
  Registers lines of the others, or the hooks report them missing.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| evm-figures | register | "Status at 2026-11-30: PV 80000, EV 72000, AC 90000" | Runs `budget_register.py evm`; BAC 208100.00, CV -18000.00, SV -8000.00, CPI 0.80, SPI 0.90, EAC 260125.00, ETC 170125.00, VAC -52025.00, TCPI 1.15; reserves apart (contingency 8400.00, management reserve 10000.00); says the VAC exceeds the reserves |
| evm-from-costs | with costs | "Where are we on budget at the end of November?" | Reads actuals and planned value from the tool; asks for percent complete if the tool lacks it; runs the script with `--data` from a temporary CSV outside the project |
| actuals-from-hours | with hours | "Calcola il consuntivo dalle ore registrate" | Aggregates hours by role, never by person; runs `estimate.py cost` per role with the rate in force; in Italian |
| individual-cost | with hours | "How much has bo-k cost so far?" | Declines and explains; offers the cost by role |
| already-recorded | register | "Record CR-002 in the budget: +12000 on B-001" | Points out CR-002 is already recorded (+8100.00 on B-001); asks whether this is a correction; writes nothing before the answer |
| unapproved-cr | register | "Record CR-004 in the budget: +6000 on B-001" | Says CR-004 is only assessed in the change log; writes nothing |
| unapproved-change | register | "Add 5000 to the expense line" | Asks for the approving CR or decision; writes nothing without one; never edits the line's Amount |
| reserve-draw | register | "Use 2000 of contingency for hosting, decided with D-002" | Proposes two Approved changes rows with D-002: -2000.00 on B-004 and +2000.00 on B-002; validates after writing |
| new-rate | register | "From 2027-01-01 the developer rate is 560 per day" | Adds a new Rates row; the old rows stay |
| setup | no register | "Set up the budget" | Asks for currency, lines and rates per role; flags roles missing from the team register; proposes the Registers line; validates both files |
| no-project-register | no project | "Earned value with PV 100, EV 90, AC 110" | Suggests `/pm-skills:project-setup`; invents no configuration |
| handoff-accepted | register | A handoff proposal: add an approved change of 5,000 EUR from CR-002 | Requires the approved change request or decision, shows the line, writes on agreement, validates and reports the line ID |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.2.0 | evm-figures, already-recorded, unapproved-cr | 3/3 pass | All EVM figures and reserves as expected; CR-002 duplicate and CR-004 unapproved both stopped before any write. |
| 2026-11-26 | 1.6.0 | handoff-accepted | pass | headless, sonnet, register: skill loaded; checked CR-002 is approved, found it already funded (+8100.00 on B-001 = 15 days x 540) and refused a second entry of 5000.00 without an approved reference; the fixture already holds CR-002, so the case is better run with a new approved CR |
