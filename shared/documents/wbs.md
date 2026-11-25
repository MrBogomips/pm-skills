# Document format: work breakdown structure (`wbs`)

A work breakdown structure decomposes the whole scope of the project into deliverables and work packages, and its
dictionary says what each work package contains and how it is accepted. It is the scope reference for the RACI
matrix, estimates and the schedule. The common rules (frontmatter, naming, versioning) are in
`shared/documents/common.md`.

## Frontmatter

The common keys, plus:

| Key | Rule |
|---|---|
| `scope-source` | the path of the document the scope comes from (the project charter or the product roadmap), relative to the project root |

## Headings

The headings below, in this order, translated into the document's language (in Italian, as
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` gives them). A heading with nothing to say keeps a one-line "nothing to
report".

```markdown
# <Project name>: work breakdown structure

## Scope reference
## Structure
## Dictionary
## Out of scope
## Sources
```

| Heading | What goes there |
|---|---|
| Scope reference | the scope source and its version, and the scope statement in two or three lines |
| Structure | the outline as a nested list, each element prefixed by its dotted ID (`1`, `1.2`, `1.2.3`); work packages are the leaves |
| Dictionary | a table `\| ID \| Work package \| Description \| Deliverable \| Acceptance \| Accountable role \| Work items \|`, one row per work package; Accountable role from the RACI matrix when declared; Work items holds the keys of the items created in the issues tool, else empty |
| Out of scope | what the scope source excludes, so that nobody decomposes it later |
| Sources | the documents, registers and tools read, with the date of the data, and the ones that could not be read |

## Rules

- The children of an element cover the whole of it and nothing more (the 100% rule); where the sources do not allow
  checking it, the document says so under the element.
- Elements are deliverables or outcomes, named with nouns, not activities; the activities that produce them belong
  to the schedule or the backlog.
- IDs are stable once the document is issued: renumbering, splitting or removing a work package is a major
  revision, and the work packages the RACI matrix references are listed in it.
