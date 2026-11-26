# Document format: meeting minutes (`meeting-minutes`)

Minutes record what a meeting decided and who does what next, so that people who were not there can act on them. The
common rules (frontmatter, naming, versioning) are in `shared/documents/common.md`.

## Frontmatter

The common keys, plus:

| Key | Rule |
|---|---|
| `meeting` | the kind or title of the meeting (`steering committee`, `kick-off with Acme Corp`) |
| `attendees` | the people present, by name or role, comma-separated; work names only, no contacts |
| `brief` | the path of the meeting brief the meeting was prepared with; absent when there was none |

`date` is the day of the meeting. The kinds of meeting, the keys, the agenda item and the link between brief and
minutes are in `shared/documents/meetings.md`.

## Headings

The headings below, in this order, translated into the document's language (in Italian, as
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` gives them):

```markdown
# <Meeting>: <date>

## Agenda
## Discussion
## Decisions
## Actions
## Risks raised
## Open questions
## Internal notes
```

| Heading | What goes there |
|---|---|
| Agenda | the items, as planned (the brief's, when there is one) or as discussed; the agenda item structure of `meetings.md` |
| Discussion | per agenda item, the points that lead to a decision or an action; not a transcript |
| Decisions | one line per decision: what, who decided; with the decision log ID once its keeper reports it |
| Actions | a table `| # | Action | Owner | Due |`, with the `AC-NNN` ID of the action log once its keeper reports it; every action has an owner and a due date, or is listed under open questions |
| Risks raised | new risks or changes to known ones, with the risk register ID once recorded |
| Open questions | what was left unresolved, and who will bring it back |
| Internal notes | last heading; notes for internal use only, for future reference: a change request not recorded, a reservation about a decision, context the client should not read. Optional: omitted when empty. `publish-deliverable` removes it before any distribution |

## Rules

- Write what was said and decided, not opinions about the people who said it.
- Leave out personal matters raised in the meeting (health, private reasons for an absence).
- Change requests raised are listed under Decisions (when decided) or Open questions, with their `CR-NNN` ID once
  its keeper reports it; one the project manager chose not to record appears only under Internal notes.
- Internal notes stay the last heading. Everything above it is written so that it can be distributed; what must not
  be distributed goes under Internal notes.
- A decision, a risk, a change request or an action recorded in a register links back to the minutes by their path.
