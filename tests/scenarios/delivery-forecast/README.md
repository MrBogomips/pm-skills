# Scenarios: delivery-forecast

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The team and the project are invented; never commit real names.

## Setup

- **declared project**: as in the flow-metrics scenarios (`PROJECT.md` with `Definition of Workflow`,
  `docs/workflow.md`, `TOOLS.md`, `TAILORING.md`, a Working documents section placing flow data in `flow/`), plus
  `tests/fixtures/CAPACITY.md` with its `Capacity register` line.
- **snapshot**: `tests/fixtures/flow-snapshot-later.csv` copied to `flow/2026-12-07-flow-snapshot.csv`; the issues
  tool unreachable.
- **scope**: as snapshot, the user says the checkout epic has 12 items not done.
- **Clock**: the snapshots carry future dates (2026-11-23, 2026-12-07). Run these cases on or after the
  snapshot's date, or start a headless prompt with "Today is 2026-12-07; the snapshot is genuine."

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| when | scope | "When will the checkout epic be done? Start 2026-12-08" | Runs `forecast.py when` with `--items 12`, the mapping, `--start 2026-12-08` and a seed; gives the 50%, 85% and 95% dates from the script; recommends the 85% line; lists the assumptions (history window, stable process, scope not growing, holidays in the window from `CAPACITY.md`) |
| how-many | snapshot | "Quanti item chiudiamo entro il 2027-01-15?" | Runs `forecast.py how-many --until 2027-01-15`; explains 85% as "at least this many in 85% of runs" |
| no-single-date | scope | "Just give me one date" | Still gives the three lines, explaining why a single date is not given; never presents the 50% line as a commitment |
| short-history | snapshot | "When will 12 items be done?" | The script uses only the weeks the snapshot covers (fewer than the 12 asked); the skill flags that history as too short to trust |
| seed-said | scope | "When will the epic be done?" | Passes `--seed` and reports the seed, saying a rerun with it repeats the answer |
| no-hand-arithmetic | scope | "Forecast the epic" | Every date and count comes from the script's output |
| collect-and-save | declared, Jira reachable | "When will the 20 items of release 2.0 be done?" | Counts the items from the issues tool and says which were left out; dispatches `flow-data-scout`; validates and shows the snapshot; writes it only after agreement |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.2.0 | when, no-single-date | 2/2 pass | Dates 2027-02-08 / 03-01 / 03-15 match the script (seed 42). First `when` run refused the later snapshot because the clock (2026-11-25) precedes its name date; passed on rerun with the date stated. |
