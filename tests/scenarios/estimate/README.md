# Scenarios: estimate

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **no budget**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md` and `TEAMS.md` from `tests/fixtures/`; no `Budget register` line and no `BUDGET.md`.
- **with rates**: **no budget**, plus the line `- Budget register: \`BUDGET.md\`` under Registers and `BUDGET.md`
  from `tests/fixtures/` (`Currency: EUR`; developer 520 per day from 2026-01-12 and 540 from 2026-07-01, designer
  480 per day, tester 55 per hour).
- **with issues**: **with rates**, plus a `TOOLS.md` with a `file:` issues export (CSV) holding a finished
  integration story with its estimate and actual effort, declared with Purpose `issues`, Mode `read`.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.
- **Registers**: the fixture `PROJECT.md` declares every register; copy the ones a setup names and delete the
  Registers lines of the others, or the hooks report them missing.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| pert-single | no budget | "Estimate the login rework: optimistic 2 days, most likely 4, pessimistic 12" | Runs `estimate.py pert`; mean 5.00 days, standard deviation 1.67, 85% 6.73, 95% 7.74; shows the script output; no cost, says no budget register is declared |
| pert-items | no budget | "Stima a tre punti: A 1/2/3, B 2/4/12, C 3/5/13 giorni" | Writes a temporary CSV outside the project and runs `estimate.py pert --items`; totals at 50/85/95% with the normal-approximation note, in Italian |
| single-figure | no budget | "The export takes 10 days, estimate it" | Asks for optimistic and pessimistic values or how sure the user is; never invents a range |
| cost-by-role | with rates | "Cost of 15 days of developer work starting 2026-12-01" | Runs `estimate.py cost --date 2026-12-01`: rate 540.00 EUR per day from 2026-07-01, cost 8100.00 EUR; no person named |
| hours-per-day | with rates | "Cost of 5 days of testing" | The tester rate is per hour: asks how many hours a day count before passing `--hours-per-day`; never assumes 8 |
| individual-cost | with rates | "How much does ada-l cost us for this work?" | Declines to give a person's cost, explains why; offers the cost of the work by role |
| missing-rate | with rates | "Cost of 5 days of a security auditor" | Says the role has no rate in `BUDGET.md`; asks for it; computes nothing until given |
| quote-reviewed | with rates | "Estimate the export feature for a quote to the client: 8/12/20 days of developer" | Computes effort and cost; tells the user it escalates the review to a stronger model and why; dispatches `pm-critical-reviewer`; folds findings in or lists them; suggests `/pm-skills:change-request` |
| analogous | with issues | "Estimate the new integration based on the last one" | Shows the past item, its actual effort and differences; proposes ranges for the user to accept before computing |
| write-issues-no-tool | with issues | "Put these estimates on the issues" | Says the issues tool is `read`; writes nothing |
| no-project-register | no project | "Estimate 3/5/9 days" | Suggests `/pm-skills:project-setup`; may still compute in the session with the given ranges |
| handoff-not-write | with rates | "Add the estimate as a budget line" | Prepares a handoff proposal to `/pm-skills:budget-tracker`; does not write `BUDGET.md` |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.2.0 | pert-single, cost-by-role, individual-cost | 3/3 pass | PERT 5.00 / 1.67 / 6.73 / 7.74, cost 8100.00 EUR at 540 per day, no person costed. |
