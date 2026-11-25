# Flow snapshot format (`flow/<YYYY-MM-DD>-flow-snapshot.csv`)

A flow snapshot is the transition history of a board's work items over a window, saved in the project so that flow
metrics and forecasts can be recomputed and compared over time. `flow-metrics`, `delivery-forecast` and
`release-plan` write it, after showing it, from the history the `flow-data-scout` agent collects. It is a data
file, not a register: it is not declared in `PROJECT.md`, and it lives where the Working documents section of
the project places data (default folder `flow/`).
The name carries the day the history was read: `2026-11-23-flow-snapshot.csv`.

A snapshot holds work items and their transitions only. It has no assignee and no person column, and its validator
rejects any column outside the header: flow metrics are team-level.

## Example

```csv
item,type,state,entered_at
ACME-101,story,To Do,2026-10-20
ACME-101,story,In Progress,2026-10-27
ACME-101,story,Review,2026-10-30
ACME-101,story,Done,2026-11-02
ACME-103,bug,In Progress,2026-11-04T09:00:00
ACME-103,bug,Done,2026-11-04T17:30:00
ACME-106,bug,In Progress,2026-10-29
ACME-106,bug,Done,2026-10-31
ACME-106,bug,In Progress,2026-11-19
```

## Fields

| Field | Meaning | Rule |
|---|---|---|
| `item` | the work item key in the issues tool | not empty |
| `type` | the item type (story, bug, task...) | not empty; the same on every row of an item |
| `state` | the state the item entered | not empty; the board's own state name |
| `entered_at` | when the item entered the state | ISO 8601 date `YYYY-MM-DD` or date-time `YYYY-MM-DDTHH:MM[:SS][Z\|+HH:MM]`; an offset is converted to UTC |

## Rules

1. CSV, UTF-8, pure (no comment lines). The header is exactly `item,type,state,entered_at`, in this order, and every
   row has four cells. Blank lines are ignored.
2. One row per transition, including the first state of the item when the history has it. No row appears twice.
3. The rows of an item are in time order (rows of different items may interleave); two rows of an item may share a
   timestamp, and then the file order decides.

## The workflow mapping

The snapshot keeps the board's states as they are. Which states mean what comes from the Definition of Workflow of
the project, or from the user, and is passed on the command line:

- `--started`: every state that means work in progress, from commitment to delivery, blocked and waiting states
  included. An item counts as work in progress on a day when its state at the end of that day is one of them.
- `--finished`: the states that mean delivered. A state cannot be in both lists; states in neither (To Do, Backlog)
  mean not started.

## Metric rules

- **Cycle time**: calendar days from the day the item first entered a started state to the day of the first
  finished state after it, both days counted (started and finished the same day = 1 day). An item that reaches a
  finished state without ever being in a started state counts in throughput but has no cycle time.
- **Reopened items**: an item that leaves a finished state keeps its first finish for cycle time and throughput,
  so reopening never rewrites past weeks; while it is back in a started state it counts as work in progress again,
  marked reopened, with its age counted from its first start. Finishing again does not count a second time.
- **Work item age**: calendar days from the first start to the day of the measure, both counted.
- **Weekly throughput**: items finished in each 7-day week; weeks are whole and end on the last day of the window,
  so the window start moves forward to the first whole week (the output says so). Weeks with no finished item count
  as 0.
- **WIP**: items in progress at the end of the day of the measure; the average is over every day of the window.
- **Percentiles**: nearest-rank: the value at rank ceil(p/100 × n) of the values sorted ascending, always one of
  the observed values. Reported at 50, 85 and 95.
- **SLE**: with `--sle-days N` (and `--sle-percent`, default 85), the share of finished items whose cycle time is at
  most N days, and the items in progress whose age is over N days.
- **Today**: the day the snapshot describes: `--today`, else the date in the file name, else the latest transition
  in the file.

## Commands

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/flow_data.py" validate <snapshot>

python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/flow_metrics.py" <snapshot> --started "In Progress,Review" \
    --finished Done [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--today YYYY-MM-DD] [--sle-days N] [--sle-percent 85]

python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/flow_metrics.py" compare <older snapshot> <newer snapshot> \
    --started ... --finished ... [--weeks N] [--old-today YYYY-MM-DD] [--new-today YYYY-MM-DD] [--sle-days N]

python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/forecast.py" when <snapshot> --items N --started ... --finished ... \
    [--type T] [--weeks-history 12] [--runs 10000] [--seed S] [--today YYYY-MM-DD] [--start YYYY-MM-DD]

python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/forecast.py" how-many <snapshot> --until YYYY-MM-DD \
    --started ... --finished ... [same options as when]
```

- `flow_metrics.py` prints, for all items and then for each item type: the finished items with their cycle time,
  the cycle time percentiles, the throughput of each week and its mean, the WIP with each item's age (reopened and
  past-SLE items marked) and the average WIP, and the SLE check. The default window runs from the first transition
  in the file to `--to` (default today). `compare` computes both snapshots with the same mapping, each over its
  own window ending on its own today (the last N weeks with `--weeks`), and prints the metrics side by side.
- `forecast.py` samples the weekly throughput of the last `--weeks-history` whole weeks ending on today (only the
  weeks the snapshot covers; `--type` counts only that item type). `when` runs weeks until N items are finished: a
  run that needs w weeks ends on `start + 7w - 1` days, start defaulting to the day after today; `p%` is the date by
  which p% of the runs finished. `how-many` adds the whole weeks from start to `--until`; `p%` means at least this
  many items in p% of the runs (the (100 - p)th nearest-rank percentile). The seed is printed: without `--seed` one
  is chosen at random, and passing it again repeats the run exactly.

Exit status 0 on success; 1 when a file holds invalid data (the errors go to stderr; `validate` prints them on
stdout as `line N: <message>`) or the history has no throughput to sample; 2 on a usage error or an unreadable file.

## DORA inputs

`dora.py` reads two temporary CSV files, built for the run from the releases, CI and incidents tools and not stored
in the project. Each has exactly this header and no other column; timestamps follow the `entered_at` rule.

| File | Header | Rules |
|---|---|---|
| Deployments | `deployed_at,commit_at,failed` | one row per production deployment; `commit_at` the time of the oldest commit deployed, may be empty; not after `deployed_at`; `failed` `yes` when the deployment caused a failure in production (rollback, hotfix, incident), else `no` |
| Incidents | `opened_at,restored_at` | one row per production incident; `restored_at` empty while not restored, never before `opened_at` |

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/dora.py" --deployments <file> [--incidents <file>] \
    --from YYYY-MM-DD --to YYYY-MM-DD
```

Deployments count when deployed, incidents when opened, between the two dates, both included. The output gives the
deployment frequency (count, per week and distinct days), the lead time for changes in hours (only deployments with
a commit time; otherwise "not available"), the change failure rate, and the time to restore service in hours with
the incidents not yet restored counted apart; percentiles are nearest-rank, as above. Exit status as above.
