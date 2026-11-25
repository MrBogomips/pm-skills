---
summary: For agile teams and their project managers - prepares a retrospective with the facts of the period and the state of the previous actions, then records keep, change and try with owned, dated actions, never about people.
---

# retrospective

Prepares and records a retrospective. Before the meeting: the facts of the sprint or period (flow, incidents,
builds, releases) and the state of the actions agreed last time. After it: what to keep, change and try, and the new
actions, each with an owner and a due date, followed up at the next retrospective.

## Why

Retrospectives fail in two ways: the same complaints come back because nobody followed up the actions, and the notes
turn into a record of who said what. This skill opens with the facts and the previous actions, so the team starts
from evidence; it writes only actions with an owner and a date; and it keeps every line about the way of working,
never about a person.

## Use cases

### Prepare the retrospective

**Context:** Sprint 14 of Acme Portal ends tomorrow; the last retrospective agreed two actions.

**Action:** Ask "prepare the retro".

**Result:** A draft with the facts of the sprint (items done against plan, items that aged, a failed release build)
and the two previous actions with their state, or "to confirm with the team" where the tools do not show it.

### Record the outcome

**Context:** After the meeting you paste the notes from the board.

**Action:** Ask "record the retrospective".

**Result:** Keep, change and try rephrased as practices, actions with a slug and a date, names and quotes removed;
with an issues tool in Mode `write`, an offer to create the actions as work items, on your confirmation.

## Usage

Ask in your own words ("retro", "prepare the retrospective", "retro actions") or run `/pm-skills:retrospective`. Say
whether you are preparing or recording; the skill asks if it cannot tell.

## Inputs and outputs

- Reads `PROJECT.md` (framework, sprint length, Definition of Workflow, naming, language, registers),
  `TAILORING.md`, `TEAMS.md`, the previous retrospective and the sprint plan, and the project's tools through
  `TOOLS.md`.
- Writes one retrospective in the folder of the project's Working documents section, named by
  `shared/scripts/doc_naming.py`, in the format of
  [`shared/documents/retrospective.md`](../../shared/documents/retrospective.md).
- On request, creates the actions as work items through an issues tool declared with Mode `write`, after you
  confirm the itemized list.

## Requirements

A project register (`/pm-skills:project-setup`). A tools register for the facts; without it the skill works from
your notes and says which sources it could not read.

## Limitations

- Works for Scrum and Kanban teams alike; without sprints the period runs from the previous retrospective.
- Flow facts are counts from the tools; cycle time and throughput analysis belong to `flow-metrics`.
- Never records who said what, and drops or rephrases any point about a person.
