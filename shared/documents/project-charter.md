# Document format: project charter (`project-charter`)

A project charter authorizes the project: why it exists, what it must achieve, what it covers and does not, the
constraints it works within, and the authority of the project manager and of the people who approve. Once issued, it
is the reference the project is held to. The common rules (frontmatter, naming, versioning) are in
`shared/documents/common.md`.

## Frontmatter

The common keys, plus:

| Key | Rule |
|---|---|
| `sponsor` | the role that sponsors the project (`Sponsor`, `Head of Digital`), not a person's contact |
| `approved-by` | the role or body that approved the charter; only with `status: issued` |
| `approved-on` | the date of the approval, `YYYY-MM-DD`; only with `status: issued` |
| `change` | on a revision after issue, the ID of the approved change that required it (`CR-004`) |

## Headings

The headings below, in this order, translated into the document's language. A heading with nothing to say keeps a
one-line "nothing to report".

```markdown
# <Project name>: project charter

## Purpose
## Objectives and success criteria
## Scope
## Deliverables and milestones
## Phases and gates
## Constraints and assumptions
## Budget summary
## High-level risks
## Stakeholders
## Authority
## Approval
## Sources
```

| Heading | What goes there |
|---|---|
| Purpose | the problem or opportunity and why the project exists now, in a few lines |
| Objectives and success criteria | measurable objectives, each with how success will be judged |
| Scope | what is in and what is out, as two lists; what is out is as explicit as what is in |
| Deliverables and milestones | the main deliverables and the milestones with their dates, from the roadmap or the schedule register |
| Phases and gates | the phases and the gates between them, in a short list; `GATES.md` holds the criteria and is authoritative |
| Constraints and assumptions | fixed dates, budget ceilings, mandated technologies or suppliers, regulations; assumptions the plan relies on |
| Budget summary | the authorized budget and reserves, from the budget register when declared |
| High-level risks | the main threats and opportunities at the start; the risk register is authoritative |
| Stakeholders | the key stakeholders as roles or groups; the stakeholder register is authoritative |
| Authority | the project manager's authority (decisions, spending, staffing), escalation path, who approves changes to scope, schedule and budget |
| Approval | the role or body that approves the charter, and the date once approved |
| Sources | the registers, documents and tools read, with the date of the data, and the ones that could not be read |

## Rules

- `approved-by`, `approved-on` and the Approval heading are filled only when the user reports the approval; the
  charter never declares itself approved.
- Summaries of registers (gates, risks, stakeholders, budget) point to the register, which prevails on any
  difference.
- An issued charter changes only through an approved change: the revision names its ID in `change`, and raises
  `version` (major for scope, objectives or authority, minor for clarifications).
- People appear as roles; no contacts, no evaluations.
