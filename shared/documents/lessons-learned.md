# Document format: lessons learned (`lessons-learned`)

A lessons learned document records what a project or a phase learned, so that the next phase, the next project or
the organization can use it: what worked, what did not, and what to do differently. It is about the way of
working, never about people. The common rules (frontmatter, naming, versioning) are in
`shared/documents/common.md`.

## Frontmatter

The common keys, plus:

| Key | Rule |
|---|---|
| `period` | the period looked back on, `YYYY-MM-DD..YYYY-MM-DD` |
| `gate` | the gate it was prepared for, as its ID in `GATES.md`; left out when it is not tied to a gate |

## Headings

The headings below, in this order, translated into the document's language (in Italian, as
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` gives them). A heading with nothing to say keeps a one-line "nothing to
report".

```markdown
# <Project name>: lessons learned <phase or period>

## Context
## What worked
## What did not work
## Recommendations
## Follow-up
## Sources
```

| Heading | What goes there |
|---|---|
| Context | the phase or period, its objectives and how it ended against them, in facts: gate outcomes, delivery, schedule and budget variance |
| What worked | practices, decisions and conditions worth repeating, each with the fact that shows it |
| What did not work | what caused delay, rework, cost or risk, each with the fact that shows it and its cause where known |
| Recommendations | what to do differently, each addressed to the next phase, the next project or the organization |
| Follow-up | a table `\| # \| Action \| Owner \| Due \|` for the recommendations the project itself will act on; Owner a role or team register slug, Due a date |
| Sources | the retrospectives, gate reviews, registers and tools read, with their date, and the ones that could not be read |

## Rules

- Points are about the way of working (process, tools, agreements, environment, decisions), never about a person.
- Nobody's words are attributed: no "who said what", no quotes with names.
- Facts are by team; a fact about one person's work is not written here.
- A follow-up action has an owner and a due date, or it is listed as a recommendation instead.
