# Document format: sprint planning (`sprint-planning`)

A sprint plan records what the Scrum Team commits to for one sprint: the Sprint Goal, the items selected to reach
it, and the capacity and readiness checks behind the selection. The common rules (frontmatter, naming, versioning)
are in `shared/documents/common.md`.

## Frontmatter

The common keys, plus:

| Key | Rule |
|---|---|
| `sprint` | the sprint as the issues tool names it (`Sprint 14`), else a number |
| `period` | the sprint's first and last day, `YYYY-MM-DD..YYYY-MM-DD`; `date` is the day of Sprint Planning |

## Headings

The headings below, in this order, translated into the document's language (in Italian, as
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` gives them). A heading with nothing to say keeps a one-line "nothing to
report".

```markdown
# <Project name>: sprint planning <sprint>

## Sprint Goal
## Capacity
## Selection
## Open points
## Risks and dependencies
## Sources
```

| Heading | What goes there |
|---|---|
| Sprint Goal | the goal in one or two sentences, as the team agreed it, and the Product Goal it serves (from the roadmap document, when there is one) |
| Capacity | a table `\| Member \| Working days \| Days off \| Allocation \| Available days \|` with a total, from the capacity register; then the recent throughput or velocity, per sprint, with the unit (items or points) |
| Selection | a table `\| # \| Item \| Title \| Estimate \| Ready \| Goal \|` in backlog order: `Ready` is `yes` or what is missing; `Goal` is `yes` when the item serves the Sprint Goal; then the selected total against the forecast from throughput or velocity |
| Open points | over-commitment and by how much, items not ready, questions the team left open, each with who brings it back |
| Risks and dependencies | what could stop the goal: external dependencies, releases, absences in the period (as availability only), with risk register IDs when recorded |
| Sources | the registers and tools read, with the date of the data, and the ones that could not be read |

## Rules

- Available days are computed, never estimated: the member's working days in the period, less the project's calendar
  `holiday` and `closure` days, times the allocation in force on each day; `event` days count as working days and
  are named as reduced.
- Absences appear only as fewer available days; a reason is never written.
- The plan is a forecast the team owns: names appear as owners of availability, never in judgments.
