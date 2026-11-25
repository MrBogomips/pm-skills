# Document format: sprint review (`sprint-review`)

A sprint review records what the sprint delivered against its Sprint Goal, what the stakeholders said about it and
how the Product Backlog changes as a result. The common rules (frontmatter, naming, versioning) are in
`shared/documents/common.md`.

## Frontmatter

The common keys, plus:

| Key | Rule |
|---|---|
| `sprint` | the sprint as the issues tool names it (`Sprint 14`), else a number |
| `period` | the sprint's first and last day, `YYYY-MM-DD..YYYY-MM-DD`; `date` is the day of the Sprint Review |
| `goal` | `met`, `partly met` or `not met` |

## Headings

The headings below, in this order, translated into the document's language. A heading with nothing to say keeps a
one-line "nothing to report".

```markdown
# <Project name>: sprint review <sprint>

## Sprint Goal
## Delivered
## Not delivered
## Feedback
## Product Backlog adaptations
## Risks and decisions
## Sources
```

| Heading | What goes there |
|---|---|
| Sprint Goal | the goal from the sprint plan, `met`, `partly met` or `not met`, and the facts behind it |
| Delivered | a table `\| Item \| Title \| Evidence \|` of the items done that meet the Definition of Done; Evidence is what shows it (merged change, release, passed check); then the releases and deployments of the sprint, with dates |
| Not delivered | a table `\| Item \| Title \| State \| Why \|` of the selected items not done, and of the items marked done that miss part of the Definition of Done; Why states facts (blocked by, reopened, scope grew), never a person's fault |
| Feedback | what the stakeholders said on the Increment, one line per point, attributed to a role or a stakeholder register ID, never to a judgment of a person |
| Product Backlog adaptations | proposed changes: new items, reordering, items dropped or split, each with the feedback or fact behind it; marked accepted or proposed |
| Risks and decisions | new risks and decisions that came up, with register IDs once recorded |
| Sources | the registers, tools, notes or minutes read, with the date of the data, and the ones that could not be read |

## Rules

- An item counts as delivered only when it meets the Definition of Done; one marked done in the issues tool that
  does not is listed under Not delivered with what it misses.
- Feedback is reported, not interpreted: what was said, by role, and what the team proposes because of it.
