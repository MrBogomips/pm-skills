# Document format: communication plan (`communication-plan`)

A communication plan says who receives what, when, through which channel and from whom, so that every stakeholder
the project depends on is reached at the right level and nobody is flooded. The common rules (frontmatter, naming,
versioning) are in `shared/documents/common.md`.

## Frontmatter

The common keys, with nothing added.

## Headings

The headings below, in this order, translated into the document's language (in Italian, as
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` gives them). A heading with nothing to say keeps a one-line "nothing to
report".

```markdown
# <Project name>: communication plan

## Audiences
## Communications
## Meetings
## Escalation path
## Sources
```

| Heading | What goes there |
|---|---|
| Audiences | a table `\| Audience \| Stakeholder \| Needs \|`: the audience as a role or group, its stakeholder register ID when declared, and what it needs to know |
| Communications | a table `\| What \| Audience \| Owner role \| Frequency \| Channel \| Produced by \|`; Frequency follows the project's `Reporting cadence` where it applies; Produced by names the document or skill that produces it (`status-report`, `sprint-review`, `meeting-minutes`) or "manual" |
| Meetings | the recurring meetings, each with its purpose, participants as roles, cadence and the record it produces |
| Escalation path | who raises what to whom, and within what time, from the team to the steering committee |
| Sources | the registers, documents and tools read, with their date, and the ones that could not be read |

## Rules

- Audiences and owners are roles or groups; no personal contacts (email addresses, phone numbers) in the plan:
  channels name the means (`steering mailing list`, `portal release notes`), never an address.
- Every active stakeholder below its desired engagement has at least one communication, or the plan says why not.
- Roles marked `C` or `I` in the RACI matrix for a deliverable are among its audiences.
