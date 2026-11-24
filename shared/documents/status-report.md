# Document format: status report (`status-report`)

A status report tells the project's stakeholders where the project stands at the end of a reporting period:
outcomes first, then the evidence. The common rules (frontmatter, naming, versioning) are in
`shared/documents/common.md`.

## Frontmatter

The common keys, plus:

| Key | Rule |
|---|---|
| `period` | the reporting period, `YYYY-MM-DD..YYYY-MM-DD`; `date` is its last day |
| `overall` | `green`, `amber` or `red` |

## Headings

The headings below, in this order, translated into the document's language. A heading with nothing to say keeps a
one-line "nothing to report" rather than disappearing, so that readers can compare reports.

```markdown
# <Project name>: status report <date>

## Summary
## Outcomes
## Schedule
## Scope
## Budget
## Risks and issues
## Decisions
## Next period
## Sources
```

| Heading | What goes there |
|---|---|
| Summary | three to five lines a sponsor reads alone: overall status and why, the main outcome, what is needed from the reader |
| Outcomes | what was delivered or achieved in the period, as outcomes (value for users or the client), before activities |
| Schedule | milestones, sprint or release progress against plan, with dates; `green`, `amber` or `red` and why |
| Scope | changes to scope in the period: accepted, pending, rejected |
| Budget | spend against budget when the project has a `costs` tool; otherwise "not tracked here" |
| Risks and issues | the risks whose score or status changed, the top open ones, the risks that occurred; IDs from the risk register |
| Decisions | decisions taken in the period, with IDs from the decision log, and decisions needed, from whom and by when |
| Next period | the outcomes planned for the next period |
| Sources | the registers and tools read, with the date of the data, and the ones that could not be read |

## Rules

- Status colors follow facts: a color without a reason is not written. `amber`: a target is at risk and a response is
  in place; `red`: a target will be missed without a decision. A project may redefine them through the `scale`
  extension point.
- Numbers come from the registers, the tools or the plugin's scripts, never from estimates made while writing.
- No names of people in judgments: delivery facts by team or by person only.
