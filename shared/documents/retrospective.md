# Document format: retrospective (`retrospective`)

A retrospective records how the team will improve its way of working: the facts of the period, the follow-up of the
previous actions, what to keep, change and try, and the actions agreed. It is about the way of working, never about
people. The common rules (frontmatter, naming, versioning) are in `shared/documents/common.md`.

## Frontmatter

The common keys, plus:

| Key | Rule |
|---|---|
| `sprint` | the sprint as the issues tool names it; left out when the team works without sprints |
| `period` | the period looked back on, `YYYY-MM-DD..YYYY-MM-DD`; `date` is the day of the retrospective |

## Headings

The headings below, in this order, translated into the document's language (in Italian, as
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` gives them). A heading with nothing to say keeps a one-line "nothing to
report".

```markdown
# <Project name>: retrospective <sprint or date>

## Facts
## Previous actions
## Keep
## Change
## Try
## Actions
## Sources
```

| Heading | What goes there |
|---|---|
| Facts | what the period shows, by team: items done against the plan, flow (work in progress, items that aged or bounced back), incidents and failed builds, releases; numbers from the tools |
| Previous actions | a table `\| # \| Action \| Owner \| Due \| State \|` with the actions of the previous retrospective; State is `done`, `in progress`, `not started` or `dropped`, with a word on why for the last two |
| Keep | practices that worked and the team wants to keep |
| Change | practices that did not work and how the team wants them to change |
| Try | experiments for the next period, each with how the team will tell whether it worked |
| Actions | a table `\| # \| Action \| Owner \| Due \|`: Owner a team register slug (or the team), Due a date; an action with no owner or date goes back to the team, it is not written |
| Sources | the registers, tools and the previous retrospective read, with the date of the data, and the ones that could not be read |

## Rules

- Points are about the way of working (process, tools, agreements, environment), never about a person.
- Nobody's words are attributed: no "who said what", no quotes with names, no counts of votes per person.
- Facts are by team; a fact about one person's work is not written here.
- Actions not finished stay visible: an action `in progress` or `not started` is carried into Actions or marked
  `dropped` by the team.
