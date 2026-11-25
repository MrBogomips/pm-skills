# Document format: product roadmap (`product-roadmap`)

A product roadmap tells the product's stakeholders where the product is going: the Product Goal, the themes that
serve it and the horizons in which they are expected, each tied to epics and releases. It separates what the team
has committed to from what it only intends. The common rules (frontmatter, naming, versioning) are in
`shared/documents/common.md`.

A roadmap is a living document: a revision changes it in place and raises `version`, and the previous versions stay
in git.

## Frontmatter

The common keys, plus:

| Key | Rule |
|---|---|
| `product` | the product the roadmap is for; the `Project name` of `PROJECT.md` when they coincide |
| `horizons` | `now-next-later`, or `dated` when the project commits dates to its horizons |

`date` is the day the roadmap was last reviewed against the facts.

## Headings

The headings below, in this order, translated into the document's language (in Italian, as
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` gives them). With `horizons: dated`, the three horizon headings become
one heading per dated horizon (`## Q1 2027`, `## Release 2.0, March 2027`), in date order. A heading with nothing to
say keeps a one-line "nothing planned" rather than disappearing.

```markdown
# <Product>: product roadmap

## Product Goal
## Themes
## Now
## Next
## Later
## Releases
## Dependencies and risks
## Changes from the previous version
## Sources
```

| Heading | What goes there |
|---|---|
| Product Goal | the one goal the product is working towards, in one or two sentences, as the Product Owner stated it |
| Themes | the outcomes that serve the Product Goal, each in one line with the problem it addresses and how its success shows |
| Now, Next, Later | per horizon, the themes or epics expected in it, each marked `committed` or `intended`, with the epic key from the issues tool when there is one |
| Releases | the releases the roadmap relies on, with their version or name, their status and, only when committed, their date |
| Dependencies and risks | what the horizons depend on (other teams, the client, suppliers, technical debt), with IDs from the risk register and decision log |
| Changes from the previous version | what moved between horizons, what was added or dropped, and why |
| Sources | the registers and tools read, with the date of the data, and the ones that could not be read |

## Rules

- **Committed or intended.** An item is `committed` only when a source says so: a release or sprint it is planned in,
  a decision in the decision log, an approved change request, a contract milestone. Everything else is `intended`.
  The Sources say where each commitment comes from.
- **No forecast.** A date appears only when the project has committed it. The roadmap does not compute or estimate
  dates; a forecast from throughput is the job of `delivery-forecast`.
- Epics, releases and IDs are those of the issues tool and the registers, never made up; an item with no epic yet
  says so.
- Ordering within a horizon and the Product Goal are the Product Owner's decisions: the document records them.
