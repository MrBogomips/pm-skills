# Schedule register format (`SCHEDULE.md`)

The schedule register keeps the project's baselines, the approved plans that progress is measured against, and,
when no schedule tool holds the plan or the tool is too simple for a critical path, the plan itself: activities,
durations and dependencies. `schedule-check` keeps it. It is declared in the Registers section of `PROJECT.md` as
`` - Schedule register: `SCHEDULE.md` ``.

Kept by: `schedule-check`. Only this skill writes the register; any other skill hands its changes off to it, as
`shared/handoff.md` says.

## Example

```markdown
# Schedule

Source: register

## Activities

| ID | Activity | Duration | Predecessors | Start | Finish | Progress |
|---|---|---|---|---|---|---|
| A-001 | Kick-off | 0 |  | 2026-01-12 | 2026-01-12 | 100 |
| A-002 | Requirements | 20 | A-001 | 2026-01-13 | 2026-02-09 | 100 |
| A-003 | Architecture | 15 | A-002 SS+10 | 2026-01-27 |  | 60 |
| A-004 | Go-live | 0 | A-003 |  | 2026-12-18 | 0 |

## Baseline B-01 Initial plan

- Approved: 2026-01-09
- Approved by: steering committee

| ID | Activity | Start | Finish |
|---|---|---|---|
| A-001 | Kick-off | 2026-01-12 | 2026-01-12 |
| A-002 | Requirements | 2026-01-13 | 2026-02-09 |
| A-003 | Architecture | 2026-01-27 | 2026-02-16 |
| A-004 | Go-live | 2026-12-18 | 2026-12-18 |
```

## Source

`Source:` says where the live plan is: `register` when it is the `## Activities` table of this file, otherwise the
name of the tool in the tools register (Purpose `schedule`) that holds it, such as `Source: Plan`. With a tool as
the source the register keeps the baselines, and `## Activities` is optional: it holds a copy of the tool's plan
when the user imports one, for instance because the tool cannot compute a critical path.

## Activities

| Column | Meaning | Rule |
|---|---|---|
| `ID` | the activity | `A-` and at least three digits, unique |
| `Activity` | what is done | not empty |
| `Duration` | working days of work | a whole number; `0` is a milestone |
| `Predecessors` | the activities it depends on | empty, or comma-separated `<ID>[ <type>[<lag>]]` |
| `Start`, `Finish` | actual or constrained dates | optional; `YYYY-MM-DD`; `Finish` not before `Start` |
| `Progress` | the share of the work done | a whole number from 0 to 100, without `%`; a milestone is `0` or `100` |

A predecessor is an ID, optionally followed by a dependency type and a lag in working days: `A-002` (finish to start,
the default), `A-002 FS+2` (two working days after A-002 finishes), `A-003 SS+5` (five working days after A-003
starts), `A-004 FF` (finishes no earlier than A-004 finishes), `A-005 FS-3` (a lead of three days). The types are
`FS`, `SS` and `FF`. An activity never depends on itself, names a predecessor once, and the dependencies never form
a cycle.

What the dates mean depends on `Progress`:

- `100`: `Start` and `Finish` are the actual dates;
- from 1 to 99: `Start` is the actual start, and `Finish` a deadline;
- `0`: `Start` is a constraint (not before that day), and `Finish` a deadline.

A milestone takes no working time: its date is the day it is reached, and when it has both dates they are the same.
There is no column for resources or people: the plan says what is done and when, never who.

## Baselines

A `## Baseline B-NN <name>` section records a plan as it was approved: `B-` and at least two digits, unique, in
increasing order, after `## Activities`. Its entries come first, then its table:

| Entry | Rule |
|---|---|
| `- Approved:` | required; `YYYY-MM-DD`; not before the approval of the previous baseline |
| `- Approved by:` | required; a role or a body, such as `steering committee` |
| `- Change:` | optional; the change request (`CR-NNN`) that led to it |

The table has the columns `ID`, `Activity`, `Start`, `Finish`: one row per activity at approval, with its planned
dates, both required, `Finish` not before `Start`. A baseline is never edited after approval: a new plan becomes a
new baseline, which supersedes the previous ones and keeps them as history.

## Rules

1. Allowed lines: the title `# Schedule`, blank lines, `Source:` before the sections, `## Activities` (required when
   the source is `register`), the baseline sections with their entries, and the tables. There are no free notes.
2. The headers are exactly the ones in the example.
3. No cell holds an email address or a phone number.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/schedule_register.py" validate <path to SCHEDULE.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
The validator reports unknown predecessors, cycles, duplicate IDs and dates out of order. It does not read the tools
register: `schedule-check` checks that a tool named as `Source` is declared there with Purpose `schedule`.

## Critical path

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/schedule_register.py" cpm <path to SCHEDULE.md> \
    [--activities <CSV>] [--capacity <path to CAPACITY.md>] [--start YYYY-MM-DD] \
    [--status-date YYYY-MM-DD] [--baseline B-NN|latest]
```

The command runs the critical path method over working days:

- **Calendar**: the working days and the `holiday` and `closure` days of the capacity register when `--capacity` is
  given, otherwise Monday to Friday with no days off. Lags count working days.
- **Start**: `--start`, else the earliest `Start` of the activities. Activities with no predecessors and no date
  start then.
- **Status date**: with `--status-date`, progress is as of the end of that day: work not started yet starts no
  earlier than the next working day, and an activity in progress finishes its remaining work (the duration times
  the share not done, rounded up) from then.
- **Passes**: the forward pass gives the early start and finish of each activity, the backward pass from the project
  finish (and from each deadline) the late start and finish. Total float is late finish minus early finish, in
  working days; it is negative when a deadline cannot be met. Activities done are reported with their actual dates
  and no float; activities in progress have no late start, since they have started.
- **Critical path**: the activities not done with a total float of zero or less, chained through the dependencies
  that drive them; every critical chain is listed (up to 20) with its lowest total float.
- **Baseline**: with `--baseline`, the start and finish variance of each activity against the named baseline (or the
  latest), in working days, positive when later than the baseline, and the variance of the end date; activities
  added or removed since the baseline are listed.

`--activities` reads the activities from a CSV file instead of the `## Activities` table, for a plan exported from
the schedule tool: UTF-8, header exactly `id,activity,duration,predecessors,start,finish,progress`, the same rules
as the table. The baselines still come from the register.

The output is plain text and shows the working: the calendar, the start and status date, a table of early and late
dates and float, the project finish, the missed deadlines, the critical paths and the variance. Exit status 0 on
success; 1 when the register, the CSV file or the capacity register is invalid (the errors go to stderr) or there
are no activities; 2 on a usage error, an unknown baseline or a file that cannot be read.
