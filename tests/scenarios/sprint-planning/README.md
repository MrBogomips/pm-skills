# Scenarios: sprint-planning

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The team and the project are invented; never commit real names.

## Setup

- **declared project**: `AGENTS.md` with `- Project register: \`PROJECT.md\`` and a `## Working documents` section
  placing documents in `docs/`; `tests/fixtures/PROJECT.md` (scrum, 2-week sprints, Definition of Done at
  `docs/definition-of-done.md`), `TOOLS.md`, `TEAMS.md`, `CAPACITY.md`, `RISKS.md` and `TAILORING.md` copied to the
  root, with the `Capacity register` line in `PROJECT.md`; a short `docs/definition-of-done.md` (merged, reviewed,
  tests pass, deployed to staging).
- **backlog**: the issues tool unreachable, so the user pastes the ordered backlog: ACME-101 (5 pts, acceptance
  criteria), ACME-102 (3 pts, acceptance criteria), ACME-103 (8 pts, no acceptance criteria), ACME-104 (5 pts,
  blocked by the payment provider), ACME-105 (3 pts); and the last three sprints done: 18, 21, 20 points.
- **no capacity**: as declared, without `CAPACITY.md` and its line.
- **kanban**: as declared, with `Agile framework: kanban` and `Definition of Workflow: \`docs/workflow.md\`` (WIP
  limit 4 in "In progress").

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| capacity-computed | declared | "Plan the sprint 2026-11-30..2026-12-11" | Per-member table computed by a script, not by hand: 9 working days after the 8 December holiday; ada-l 5, bo-k 7.2, cy-t 4.5, total 16.7; no reason for any absence |
| forecast-scaled | declared, backlog | "Plan the sprint 2026-11-30..2026-12-11" | Average of 18, 21, 20 points, scaled by available days with the arithmetic shown; unit named as points |
| goal-proposed | declared, backlog | "Pianifica lo sprint" | One to three candidate goals tied to the top of the backlog; waits for the user's choice before drafting the goal |
| over-commitment | declared, backlog | "Plan the sprint with all five items" | Flags over-commitment and by how much against the forecast |
| not-ready | declared, backlog | "Plan the sprint" | ACME-103 and ACME-104 marked not ready with what is missing; suggests `/pm-skills:backlog-refinement` |
| applies-tailoring | declared, a `## sprint-planning` section in `TAILORING.md` | "Plan the sprint" | Says which rules it applies |
| no-capacity-register | no capacity | "Plan the sprint" | Says there is no capacity register, asks for availability or plans without it, suggests `/pm-skills:capacity-register` |
| write-sprint-confirmed | declared, Jira reachable | "Plan the sprint", agree, then "create it in Jira" | Shows an itemized list (sprint, goal, dates, each item) and writes only what is confirmed; the plan written with `status: draft` only after agreement |
| kanban-replenishment | kanban | "Sprint planning" | Says in two lines there is no sprint; proposes the items to pull against the WIP limit; writes nothing |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.1.0 | capacity-computed + forecast-scaled + not-ready (Jira unreachable, backlog pasted) (headless, sonnet, writes disallowed) | pass | Said Jira could not be read; capacity 16.7 (5, 7.2, 4.5); forecast 11.7 pts; 103 and 104 not ready, suggested backlog-refinement |
