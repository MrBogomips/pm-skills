# Scenarios: capacity-register

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **no register**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md` and `TEAMS.md` from `tests/fixtures/`; no `Capacity register` line and no `CAPACITY.md`.
- **declared**: **no register**, plus the line `- Capacity register: \`CAPACITY.md\`` under Registers and a
  `CAPACITY.md` with the default working days; Calendar: 2026-12-08 holiday, 2026-12-24 to 2026-12-31 closure,
  2026-12-11 event (all-hands); Allocation: ada-l from 2026-01-12 at 100, bo-k from 2026-02-01 at 50, cy-t from
  2026-09-01 at 100, and a period for cy-t 2026-12-14 to 2026-12-15 at 0.
- **with calendar**: **declared**, plus a `TOOLS.md` with a `file:` calendar (an `.ics` or spreadsheet with
  national holidays and two absences) declared with Purpose `calendar`, Mode `read`.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| setup-from-team | no register | "Set up the capacity register" | Proposes `CAPACITY.md` with both sections and a base row for each active member of the team register, asking for each allocation instead of assuming 100; proposes the Registers line; writes after the user agrees; both files validate |
| absence-without-reason | declared | "Registra l'assenza di bo-k dal 2 al 4 dicembre, ha un'operazione" | Proposes a period row bo-k 2026-12-02 to 2026-12-04 at 0; leaves out the reason and says why, in Italian |
| overlap-rejected | declared | "cy-t is away from 2026-12-15 to 2026-12-17" | Detects the overlap with the period ending 2026-12-15; proposes merging or splitting; writes nothing before the user chooses |
| allocation-change-new-row | declared | "From 2027-01-04 bo-k is on the project full time" | Adds a new base row bo-k from 2027-01-04 at 100; the old base row stays |
| unknown-member | declared | "Add a base allocation for di-r at 50% from 2026-12-01" | Flags that di-r left on 2026-06-30 per the team register; suggests `/pm-skills:team-register` if that is wrong; writes nothing unless the user confirms |
| import-holidays | with calendar | "Import the holidays until the end of the project" | Reads the calendar tool up to `Planned end date`; shows an itemized list of project-wide days not already recorded; writes only confirmed rows; absences are not imported as calendar days |
| import-without-tool | declared | "Import the holidays from the calendar" | Says no `calendar` tool is declared, names the source it could not read, offers to record what the user gives |
| person-days-member | declared | "How many person-days does bo-k have from 2026-12-07 to 2026-12-18?" | Computes with a short script: 10 working days, minus the 2026-12-08 holiday, at 50%: 4.5; shows the working days, the day off and the allocation segment; lists the 2026-12-11 event as not subtracted |
| person-days-team | declared | "Team capacity from 2026-12-07 to 2026-12-18" | ada-l 9, bo-k 4.5, cy-t 7 (9 minus the 2-day period at 0), team 20.5, with the computation shown per member |
| no-project-register | no project | "Add a holiday on 2026-12-08" | Suggests `/pm-skills:project-setup`; goes on only on a path the user names; invents no configuration |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.1.0 | person-days-member (headless, sonnet, writes disallowed) | pass | 4.5 with 9 counted days, 12-08 off, 50% segment; 12-11 event listed as not subtracted |
