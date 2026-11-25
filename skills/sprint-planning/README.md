---
summary: For Scrum teams and their project managers - drafts the sprint plan with a Sprint Goal tied to the Product Goal and a selection checked against computed capacity, recent throughput and readiness.
---

# sprint-planning

Drafts the sprint plan: the Sprint Goal, the items selected to reach it, the team's capacity for the sprint and the
open points (over-commitment, items not ready, risks to the goal). Capacity comes from the capacity register,
throughput or velocity from the issues tool, readiness from the Definition of Done.

## Why

A sprint planned on gut feeling overcommits in the sprint with a holiday in it, and discovers in the middle that half
the items were never ready. This skill computes the available days from allocations and the project calendar,
scales the forecast from recent sprints, ties candidate goals to the Product Goal, and flags what does not fit before
the team commits. It writes the sprint into the issues tool only on your confirmation, item by item.

## Use cases

### Plan a sprint with a holiday in it

**Context:** Acme Portal runs two-week sprints; the next one includes 8 December, a calendar day off, and `bo-k` is
at 50% that sprint.

**Action:** Ask "plan sprint 15".

**Result:** A capacity table with the day off and the reduced allocation, a forecast scaled from the last three
sprints, candidate goals to choose from and a selection that stops at the forecast; anything beyond it is flagged as
over-commitment.

### Catch items that are not ready

**Context:** The top of the backlog holds two items with no acceptance criteria.

**Action:** Ask "pianifica lo sprint".

**Result:** The two items appear with `Ready` saying what is missing, under Open points, with a suggestion to run
`/pm-skills:backlog-refinement`.

### A Kanban team

**Context:** The project declares `Agile framework: kanban`.

**Action:** Ask "sprint planning".

**Result:** A short answer that there is no sprint, and a proposed replenishment against the WIP limits of the
Definition of Workflow.

## Usage

Ask in your own words ("plan the next sprint", "obiettivo dello sprint") or run `/pm-skills:sprint-planning`. Say
the sprint if you know it; otherwise the skill finds it in the issues tool or proposes it.

## Inputs and outputs

- Reads `PROJECT.md` (framework, sprint length, Definition of Done, naming, language, registers), `TAILORING.md`,
  `CAPACITY.md`, `TEAMS.md`, `RISKS.md`, the latest roadmap and previous sprint documents, and the issues tool
  through `TOOLS.md`.
- Writes one plan in the folder of the project's Working documents section, named by
  `shared/scripts/doc_naming.py`, in the format of
  [`shared/documents/sprint-planning.md`](../../shared/documents/sprint-planning.md).
- On request, creates the sprint and adds its items through an issues tool declared with Mode `write`, after you
  confirm the itemized list.

## Requirements

A project register (`/pm-skills:project-setup`) with `Sprint length`, and a tools register with an `issues` tool.
A capacity register (`/pm-skills:capacity-register`) for capacity; without it the skill asks or plans without it.

## Limitations

- The forecast is a simple average of recent sprints scaled by availability; probabilistic forecasts belong to
  `delivery-forecast`.
- Readiness is judged on what the issues tool shows against the Definition of Done; a missing DoD file narrows the
  check.
- Never changes the backlog, its order or its estimates.
