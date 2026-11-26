---
name: sprint-planning
description: Drafts the sprint plan - a Sprint Goal proposed from the Product Goal and the ordered backlog, a selection checked against the team's capacity and recent throughput or velocity, items not ready and over-commitment flagged - and writes the sprint to the issues tool on confirmation. Use to plan a sprint ("sprint planning", "plan the next sprint", "Sprint Goal").
---

# Sprint planning

Prepares Sprint Planning and records its outcome: a Sprint Goal, the items selected for it, and the capacity and
readiness checks that show whether the selection holds. The team decides; the skill proposes and checks.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **The project register**: `PROJECT.md`, declared by `` - Project register: `PROJECT.md` `` in the project's
  `AGENTS.md` (or `CLAUDE.md`): `Project name`, `Internal code`, `Deliverable language`, the Profile keys
  `Agile framework`, `Sprint length`, `Definition of Done`, `Definition of Workflow`, the naming Conventions and the
  Registers. With no project register, suggest `/pm-skills:project-setup`; you may still draft in the session if the
  user wants, asking for what you would have read there and inventing no configuration.
- **Registers**, when declared: capacity register (format `${CLAUDE_PLUGIN_ROOT}/shared/registers/capacity.md`),
  team register, risk register, tools register, tailoring register.
- **Documents**: the latest product roadmap (the Product Goal), the previous sprint plan and sprint review, found in
  the documents folder by the naming convention.
- **Tool capabilities** (through `TOOLS.md`): `issues` for the ordered backlog, estimates, sprints and their
  completed work; `releases` and `calendar` when declared.
- **Formats**: `${CLAUDE_PLUGIN_ROOT}/shared/documents/sprint-planning.md` and
  `${CLAUDE_PLUGIN_ROOT}/shared/documents/common.md`.

## Steps

1. **Read the configuration** and the `## sprint-planning` section of `TAILORING.md`; say which rules you will
   apply.
2. **Kanban.** With `Agile framework: kanban`, say in two lines that there is no sprint to plan, and offer instead a
   replenishment: the items to pull next, in backlog order, against the WIP limits and pull policies of the
   Definition of Workflow (else the board's configuration). Show it as a list; write nothing unless asked. Stop here.
3. **Set the sprint.** From the issues tool (the next or newly created sprint) or from the previous sprint plan and
   `Sprint length`: name, first and last day. With neither, propose them and ask.
4. **Capacity.** Run
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/capacity_register.py" available <CAPACITY.md> --from <first day> --to <last day>`
   and show its per-member table, never computed by hand; treat `event` days as the format says. With no capacity
   register, say so, ask for the availability or plan without it, and suggest
   `/pm-skills:capacity-register`.
5. **Throughput or velocity.** From the issues tool, the items (or points, if the team estimates in points) done in
   each of the last three sprints, and the average. Say which unit you used and why; with fewer than three sprints,
   say so. Scale the forecast by this sprint's available days against the usual ones, and show the arithmetic.
6. **Propose the Sprint Goal** with the team: one to three candidate goals, each tied to the Product Goal (when a
   roadmap exists) and to the top of the ordered backlog. The user chooses or rewrites it; never write a goal they
   did not accept.
7. **Select and check.** In backlog order, the items that serve the goal, up to the forecast. For each, readiness:
   clear enough to meet the Definition of Done within the sprint (acceptance criteria, estimate, no open blocking
   dependency). Read the Definition of Done file; if it is missing, say so and check only what the issues tool shows.
   Flag:
   - **over-commitment**: the selection beyond the forecast, by how much;
   - **items not ready**, with what is missing, and suggest `/pm-skills:backlog-refinement`;
   - risks to the goal: external dependencies, releases due, low availability, open high risks.
8. **Draft** in the format, in the `Deliverable language`. Keep facts (tool data, computed numbers) apart from what
   you inferred. Put in Sources what was read, with the date of the data, and what could not be read.
9. **Name and show.** Name the file with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/doc_naming.py" next --project <PROJECT.md> --dir <folder> --type sprint-planning --date <planning day>`
   (exit status 3: a plan exists for that date; revise it instead). Show the draft and the path; write it with
   `status: draft`, `version: 1.0.0` only after the user agrees, and set `status: issued` when they approve it.
10. **Write the sprint to the issues tool**, only when the user asks and only through an `issues` tool with
    `Mode: write`: show the itemized list (create or name the sprint, set its goal and dates, add each item) and make
    only the writes the user confirms on that list. Report each write and any that failed.

## Always

- Show the capacity and forecast arithmetic, so the team can check it.
- Absences appear only as fewer available days; never ask for or write a reason.
- Delivery facts by team; names only as owners of availability or items, never in judgments.
- Name every source that could not be read and what the plan cannot say because of it.

## Never

- Never set a Sprint Goal or a selection the team did not accept: the plan is the team's forecast.
- Never change the backlog, its order or its estimates; suggest `/pm-skills:backlog-refinement` instead.
- Never write to the issues tool without a `Mode: write` tool and the user's confirmation on the itemized list.
- Never write to the registers from here: propose a handoff to the keeper (`${CLAUDE_PLUGIN_ROOT}/shared/handoff.md`)
  for what should go in the risk register or the capacity register, and hand it over only when the user agrees.
  Follow-ups for the project manager may go to `/pm-skills:action-log`.

## Extension points

- `format`: sections added to or renamed in the plan, or a project template.
- `scale`: the over-commitment threshold, the number of past sprints for the forecast, the unit (items or points).
- `rules`: extra readiness checks, such as a Definition of Ready, or an approval before the plan is issued.
- `steps`: extra steps before proposing the goal, before drafting, or after issuing.
- `terms`: the project's words for the sprint, the goal and the plan.
