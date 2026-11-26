# Document format: meeting brief (`meeting-brief`)

A brief prepares the project manager for a meeting: what to achieve, who is in the room, what each agenda item must
produce and which open points to bring. It is a working document for the project manager, written before the
meeting. What it shares with the minutes (kinds, keys, agenda item, link) is in `shared/documents/meetings.md`;
the common rules are in `shared/documents/common.md`.

## Frontmatter

The common keys, plus `meeting` and `attendees` as `meetings.md` gives them. `date` is the day of the meeting.

## Headings

The headings below, in this order, translated into the document's language (in Italian, as
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` gives them):

```markdown
# <Meeting>: <date>

## Objective
## Attendees
## Agenda
## Content brief
## Open items
## Pre-reads
```

| Heading | What goes there |
|---|---|
| Objective | one or two sentences: what the meeting must achieve, and the outcome that would make it a success |
| Attendees | a table `\| Role or name \| Stakeholder \| Interest in the meeting \|`: the stakeholder register ID when declared; roles and levels only, never contacts |
| Agenda | a table `\| # \| Item \| Time \| Owner \| Decision sought \|`; the times add up to the length of the meeting |
| Content brief | per agenda item, the facts to present, the position to take and the questions to expect; short |
| Open items | what the registers say is open and relevant, each with its ID: actions due or overdue, decisions pending or taken since the last meeting, risks to review or high, change requests to decide, gates near, open questions of the previous minutes |
| Pre-reads | the documents to send before the meeting, each with its path or link, whom it goes to and by when |

## Rules

- Every agenda item has a decision sought, or says `information only`.
- Open items are copied from the registers as they stand at the date of the brief, with their IDs; the brief
  records nothing in them. A new point found while preparing goes to the keeper by handoff.
- The brief is internal: it may hold the project manager's position and expected objections, so it is not
  distributed as it is.
- The facts come from the registers and the tools; say which could not be read.
