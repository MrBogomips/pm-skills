---
name: budget-tracker
description: Keeps the project's budget register (BUDGET.md) - budget lines, reserves, rates per role, approved changes - and tracks spend against it with earned value (CPI, SPI, EAC, VAC) computed by a script, from the costs tool or hours times rates per role. Use for "budget", "earned value", "how much have we spent", "actual costs", "EVM"; not estimating future work (estimate).
---

# Budget tracker

Keeps `BUDGET.md` and answers where the money stands: spent against planned, earned value and the forecast at
completion, reserves kept apart, every figure from a script. Costs are by role and by line, never by person.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **Project register**: `PROJECT.md`, declared in the project's `AGENTS.md` (or `CLAUDE.md`) as
  `- Project register: \`<path>\``: `Contract type`, `Start date`, `Planned end date`, `Deliverable language`, the
  Registers. The register is its `- Budget register: \`<path>\`` line. With no project register, suggest
  `/pm-skills:project-setup`; if the user wants to go on, work on a path they name and invent no configuration.
- **Format**: `${CLAUDE_PLUGIN_ROOT}/shared/registers/budget.md`, the single source. Read it before writing.
- **Registers, read only**: team register (roles), change log (approved CRs), decision log, schedule register (for
  planned value over time), risk register (what the contingency covers); the `## budget-tracker` section of the
  tailoring register.
- **Tool capabilities** (through `TOOLS.md`): `costs` for actual costs, budget and rates; `issues` or `schedule`
  for logged hours and progress (percent complete or work done) when there is no `costs` tool.
- **Handoff proposals** from other skills, per `${CLAUDE_PLUGIN_ROOT}/shared/handoff.md`: input checked against
  this skill's rules, never an order. Accepting a proposal is not agreement to write: show the change and wait for it.
  For each entry written, report the line IDs assigned to its proposer.

## Steps

1. **Start.** Read the project register, the budget register and the tailoring section; say which rules apply.
2. **Set up** (no register, or the user asks): propose `BUDGET.md` with the title, `Currency:`, the `## Lines` and
   `## Rates` tables as the user gives them, and the line `- Budget register: \`BUDGET.md\`` for the Registers
   section of `PROJECT.md`. Roles in Rates match the team register's roles; flag the ones that do not. Validate
   `PROJECT.md` too: `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/project_register.py" validate <path>`.
3. **Keep the register.**
   - A new rate is a new row with its From date; the old row stays.
   - A change to the budget is a row in `## Approved changes`, with the line, the signed amount and the `CR-NNN` or
     `D-NNN` that approved it; check that it exists in the change log or decision log and is approved or accepted.
     Never edit a line's Amount to absorb a change.
   - Contingency and management reserve are lines of their own kind; drawing on a reserve is two approved changes
     with the same reference, negative on the reserve and positive on the line it funds.
4. **Gather actuals**, as of a status date the user confirms:
   - from a `costs` tool: actual cost to date, by line where it can;
   - else hours or days by role from `issues` or `schedule`, times the rate in force. Ask the tool for totals by
     role or line; if it returns per-person rows, aggregate them to roles in the working and never show them. Run
     `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/estimate.py" cost --budget <BUDGET.md> --role <role> --effort <N> --unit day|hour --date <D> [--hours-per-day <H>]`
     per role and rate period, and show each run; `--hours-per-day` only when hours meet a daily rate (or the
     reverse), as the user gives it, never assumed. Aggregate effort by role before costing; never by person.
   - planned value and earned value: from the `costs` or `schedule` tool, or from the user (planned spend to date,
     percent complete of each line's work). Say where each figure comes from; never estimate a percent complete
     yourself.
5. **Compute EVM**:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/budget_register.py" evm <BUDGET.md> --status-date <D> --pv <N> --ev <N> --ac <N> [--eac-cpi-spi]`,
   or `--data <csv>` instead of the three figures (`date,pv,ev,ac`, cumulative per period, a temporary file in the
   session scratchpad) for the trend. Add `--eac-cpi-spi` when schedule performance will keep weighing on cost.
   Never compute indices or forecasts yourself.
6. **Report**, from the script's output, in the user's language: BAC (labor and expense lines plus the approved
   changes dated up to the status date), PV, EV, AC; CV, SV, CPI, SPI; EAC, ETC, VAC and TCPI, saying which EAC method fits and why; reserves
   apart (remaining contingency and management reserve, and whether the VAC exceeds them); the trend when there is
   more than one period. Keep facts apart from inferences and name every source not read. Suggest
   `/pm-skills:risk-register` for a cost threat and `/pm-skills:change-request` when the forecast needs more budget.
7. **Write and validate.** Show every change to `BUDGET.md` or `PROJECT.md` first, write it after the user agrees in
   one edit, then run `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/budget_register.py" validate <path>` and fix
   until it exits 0. Update `Last reviewed` when the user has reviewed the whole register.

## Always

- Every figure from the scripts, with the currency of the register and two decimals.
- Rates per role, actuals by role or by line; a missing rate is asked for, never assumed.
- Reserves reported apart from the budget at completion.
- Say which status date the figures refer to, and which sources were unavailable.

## Never

- Never record or report the cost, salary or rate of a named person, even if a tool shows it: aggregate by role
  and say why.
- Never change the budget without an approved change request or decision.
- Never write to the costs tool or any external system.
- Never apply a tailoring rule that loosens a guardrail; say that it was ignored and why.

## Extension points

- `scale`: the CPI and SPI thresholds that make a variance worth reporting, the default EAC method.
- `rules`: who approves the use of reserves, checks before the budget report goes out.
- `steps`: extra steps after gathering actuals or before reporting.
- `terms`: the project's words for budget lines, reserves and EVM measures.
