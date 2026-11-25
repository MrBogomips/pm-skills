---
summary: For project managers - keeps CAPACITY.md, the project calendar and each member's allocation and absences with no reasons, and answers how many person-days a member or the team has in a period, with the computation shown.
---

# capacity-register

Keeps `CAPACITY.md`, the project's capacity register: the working calendar (holidays, closures, events) and how much
of each member's time goes to the project, period by period. It imports holidays and absences from the project's
calendar, checks members against the team register, and answers availability questions from the register.

## Why

Sprint plans and change impacts go wrong when nobody remembers the closure between Christmas and New Year or that a
tester is on the project half time. This skill keeps those facts in one validated file, as dates and percentages
only, so that `sprint-planning` and your own questions get the same answer. Reasons for an absence never enter the
file, even when you mention them.

## Use cases

### Import the holidays for the rest of the year

**Context:** `TOOLS.md` declares the team calendar with Purpose `calendar`.

**Action:** Ask "import the holidays until the end of the project".

**Result:** An itemized list of project-wide days off from the calendar, minus those already recorded; the ones you
confirm are added to the Calendar section.

### Record an absence

**Context:** bo-k will be away from 7 to 18 December for health reasons.

**Action:** Ask "registra l'assenza di bo-k dal 7 al 18 dicembre, è malato".

**Result:** A period row for bo-k at 0% from 2026-12-07 to 2026-12-18, checked against bo-k's other periods; the skill
says the reason was left out and why.

### Team capacity for the next sprint

**Context:** Sprint 14 runs from 2026-12-07 to 2026-12-18.

**Action:** Ask "how many person-days does the team have in sprint 14?".

**Result:** The total per member and for the team, with the working days, the calendar days off and each allocation
segment shown, so you can check the number.

## Usage

Ask in your own words ("add a holiday", "giorni disponibili di ada-l a dicembre") or run
`/pm-skills:capacity-register`. Without a register the skill starts by setting one up from the team register.

## Inputs and outputs

- Reads `PROJECT.md` (declared in `AGENTS.md` or `CLAUDE.md`), the `capacity-register` section of `TAILORING.md`,
  the team register, and a calendar tool as listed in `TOOLS.md`.
- Writes `CAPACITY.md` in the format of [`shared/registers/capacity.md`](../../shared/registers/capacity.md), and
  once, with your consent, the `Capacity register` line in `PROJECT.md`.
- Never writes to the calendar tool.

## Requirements

A project register (`/pm-skills:project-setup`) and, for member checks, a team register
(`/pm-skills:team-register`). The calendar tool is optional: without it the skill records what you tell it.

## Limitations

- Allocation is a percentage of a member's working time; hours, part days and time zones are not modelled.
- Calendar days are project-wide; a member's own day off is a period at 0%.
- `event` days are listed but not subtracted from capacity unless you decide otherwise.
