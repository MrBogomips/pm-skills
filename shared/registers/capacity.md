# Capacity register format (`CAPACITY.md`)

The capacity register records how much of each team member's working time goes to the project, and the days when
the whole project works less: holidays, closures, events. Planning skills read it to size sprints and check dates.
`capacity-register` keeps it. It is declared in the Registers section of `PROJECT.md` as
`` - Capacity register: `CAPACITY.md` ``.

Kept by: `capacity-register`. Only this skill writes the register; any other skill hands its changes off to it, as
`shared/handoff.md` says.

## Example

```markdown
# Capacity

Working days: mon, tue, wed, thu, fri

## Calendar

| From | To | Kind | Description |
|---|---|---|---|
| 2026-12-08 |  | holiday | Public holiday |
| 2026-12-24 | 2027-01-06 | closure | Winter closure |
| 2026-11-27 |  | event | Company all-hands, afternoon only |

## Allocation

| Member | From | To | Allocation |
|---|---|---|---|
| ada-l | 2026-01-12 |  | 100 |
| bo-k | 2026-02-01 |  | 50 |
| bo-k | 2026-09-01 |  | 80 |
| ada-l | 2026-12-01 | 2026-12-05 | 0 |
```

Here `bo-k` works half time on the project from February and 80% from September; `ada-l` is away in the first
week of December.

## Fields

| Field | Meaning | Rule |
|---|---|---|
| `Working days` | the days of the week the project works | optional, default `mon, tue, wed, thu, fri`; comma-separated `mon` … `sun`, each once |
| Calendar `From`, `To` | the first and last day of a project-wide non-working or reduced period | `YYYY-MM-DD`; `To` empty for a single day, otherwise not before `From` |
| Calendar `Kind` | `holiday` and `closure` are days off; `event` is a day of reduced time (an all-hands, an offsite) | `holiday`, `closure` or `event` |
| Calendar `Description` | what the day is | not empty |
| Allocation `Member` | the team member | a team register slug |
| Allocation `From`, `To` | when the allocation applies | `YYYY-MM-DD`; `To` not before `From` |
| Allocation `Allocation` | the share of the member's working time on the project | a whole number from 0 to 100, without `%` |

A row with an empty `To` is a **base allocation**: it holds from `From` until the next base row of the same member.
A row with `To` is a **period** that overrides the base for those days; an absence is a period at `0`.

## Rules

1. Allowed lines: the title `# Capacity`, blank lines, `Working days:` before the sections, and the two sections
   `## Calendar` and `## Allocation`, in this order, each with its table. There are no free notes.
2. The headers are exactly the ones in the example.
3. Two base rows of the same member never share `From`; two periods of the same member never overlap.
4. The register never says why someone is away or works less: there is no column for reasons, and descriptions
   are about project-wide days only. No cell holds an email address or a phone number.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/capacity_register.py" validate <path to CAPACITY.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
The validator does not read the team register: `capacity-register` checks that every member is one of its slugs.

## Available person-days

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/capacity_register.py" available <path to CAPACITY.md> \
    --from YYYY-MM-DD --to YYYY-MM-DD [--member <slug>]
```

The command counts, for each member (or the one named) and for the team, the person-days available between the
two dates, both included:

- a day counts when it is a working day and not a `holiday` or `closure` of the calendar; `event` days count as
  normal and are listed apart;
- each counted day weighs the member's allocation that day: a period covering it, else the latest base row in
  effect, else 0.

The output is plain text and shows the working: the working days, the days off excluded, the events, then for each
member the segments of equal allocation with their days and person-days, then the total. Exit status 0 on success;
2 on a usage error, an unreadable file, an invalid register (the validation errors go to stderr) or a member with
no allocation rows.
