# Document format: phase gate review (`phase-gate-review`)

A phase gate review assesses the project's readiness to pass a gate (or to close) against the gate's criteria in
the gate register, with the evidence for each, and gives the people who decide a recommendation. It records their
decision once they have taken it. The common rules (frontmatter, naming, versioning) are in
`shared/documents/common.md`.

## Frontmatter

The common keys, plus:

| Key | Rule |
|---|---|
| `gate` | the gate assessed, as its ID in `GATES.md` (`G-002`) |

`date` is the day of the assessment.

## Headings

The headings below, in this order, translated into the document's language. A heading with nothing to say keeps a
one-line "nothing to report".

```markdown
# <Project name>: gate review <gate ID> <gate name>

## Gate and criteria
## Assessment
## Open conditions
## Risks and issues for the decision
## Recommendation
## Decision
## Sources
```

| Heading | What goes there |
|---|---|
| Gate and criteria | the gate, its milestone and planned date, and who decides it: the charter's Authority, else the decider of earlier outcomes, else the user's answer |
| Assessment | a table `\| # \| Criterion \| Assessment \| Evidence \|`, one row per criterion of `GATES.md`; Assessment is `met`, `partly met`, `not met` or `no evidence`; Evidence names the fact and its source |
| Open conditions | the conditions of earlier outcomes of this gate, each with its state from the facts, or "to confirm" when the facts do not show it |
| Risks and issues for the decision | open high risks, pending changes and known issues that bear on the decision, from the registers |
| Recommendation | `go`, `go with conditions`, `hold` or `stop`, with its reasons and, for conditions, what and by when |
| Decision | filled only once decided: the outcome, who decided it, the date and the conditions, as recorded in `GATES.md`; until then "pending" |
| Sources | the registers, documents and tools read, with the date of the data, and the ones that could not be read |

## Rules

- Every criterion of the gate is assessed; a criterion without evidence is `no evidence`, never `met`.
- The Recommendation is never written as the Decision: the Decision comes only from the user's report of what the
  people with the authority decided.
- Filling the Decision is a patch revision of the document.
- Assessments are about the project's work and its evidence, never about people.
