# Document format: meeting minutes (`meeting-minutes`)

Minutes record what a meeting decided and who does what next, so that people who were not there can act on them. The
common rules (frontmatter, naming, versioning) are in `shared/documents/common.md`.

## Frontmatter

The common keys, plus:

| Key | Rule |
|---|---|
| `meeting` | the kind or title of the meeting (`steering committee`, `sprint review`, `kick-off with Acme Corp`) |
| `attendees` | the people present, by name or role, comma-separated; work names only, no contacts |

`date` is the day of the meeting.

## Headings

The headings below, in this order, translated into the document's language:

```markdown
# <Meeting>: <date>

## Agenda
## Discussion
## Decisions
## Actions
## Risks raised
## Open questions
```

| Heading | What goes there |
|---|---|
| Agenda | the items, as planned or as discussed |
| Discussion | per agenda item, the points that lead to a decision or an action; not a transcript |
| Decisions | one line per decision: what, who decided; with the decision log ID once it is recorded |
| Actions | a table `| # | Action | Owner | Due |`; every action has an owner and a due date, or is listed under open questions |
| Risks raised | new risks or changes to known ones, with the risk register ID once recorded |
| Open questions | what was left unresolved, and who will bring it back |

## Rules

- Write what was said and decided, not opinions about the people who said it.
- Leave out personal matters raised in the meeting (health, private reasons for an absence).
- A decision or a risk recorded in a register links back to the minutes by their path.
