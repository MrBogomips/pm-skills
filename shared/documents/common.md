# Documents: common rules

A document is a snapshot of the project at a date: a status report, meeting minutes, a charter. Its format lives in
`shared/documents/<type>.md`: the type's own frontmatter keys, if any, and its fixed headings. This file holds what
every type shares: the frontmatter, the naming, the versioning and where documents go. Documents have no validator
and no hook.

## Frontmatter

```yaml
---
type: status-report
project: ACME
date: 2026-11-24
version: 1.0.0
status: draft
language: English
---
```

| Key | Rule |
|---|---|
| `type` | the document type, the name of its format file (`status-report`) |
| `project` | the `Internal code` of `PROJECT.md`, or its `Project name` when there is no code |
| `date` | the date the document refers to (`YYYY-MM-DD`): the meeting, the end of the reporting period |
| `version` | semver, always present: `1.0.0` for a first issue |
| `status` | `draft` until the user approves it, then `issued` |
| `language` | the language the document is written in: the `Deliverable language` of `PROJECT.md`, else the user's |

A type adds its own keys after these (see its format). Keys stay in English; values follow the document's language.

## Naming

The `Naming` key in the Conventions of `PROJECT.md` picks the preset; with no key, `by date`.

| Preset | Pattern | Example |
|---|---|---|
| `by date` | `<type>/<date>-<type>[-<slug>].md` | `status-report/2026-11-24-status-report.md` |
| `coded` | `<PROJ>-<CODE>-<NNN>[-<slug>].md` | `ACME-SR-007.md` |

`<PROJ>` is the `Internal code`; `NNN` is a number per type, one more than the highest in the folder. A type's
`<CODE>` comes from `Type codes` in Conventions, else from the defaults:

| Type | Code | Type | Code |
|---|---|---|---|
| `status-report` | `SR` | `retrospective` | `RT` |
| `meeting-minutes` | `MM` | `product-roadmap` | `RM` |
| `project-charter` | `PC` | `release-plan` | `RP` |
| `lessons-learned` | `LL` | `wbs` | `WBS` |
| `sprint-planning` | `SP` | `communication-plan` | `CP` |
| `sprint-review` | `SV` | `team-charter` | `TC` |
| `phase-gate-review` | `GR` | | |

With `Version in file name: yes`, the name ends in the version (`ACME-SR-007-1.2.0.md`) and a `+N` suffix avoids a
collision. A distribution format (Word, PDF) keeps the base name of its Markdown source.

The name is computed, never made up:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/doc_naming.py" next --project <PROJECT.md> --dir <folder> \
  --type <type> [--date YYYY-MM-DD] [--slug <slug>] [--version X.Y.Z]
```

It prints the path relative to the folder; exit status 3 means that name is taken (give a slug, or revise the
existing document instead).

## Versioning

Projects are under git, which keeps every version; a revision changes the document in place and raises `version`:

- **major** for a change of content or structure;
- **minor** for compatible extensions and clarifications;
- **patch** for form and formatting.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/doc_naming.py" bump <version> major|minor|patch
```

When the version is in the file name, a revision is a new file with the new version, and the old one stays.

## Where documents go

In the folder the project's Working documents section (in `AGENTS.md` or `CLAUDE.md`) gives for the type, or for
documents in general. With no such section, ask the user once and suggest recording the answer there.

## Writing

- Deliverables are Markdown; Word, PDF, slides and artifacts are generated from it only when the user asks to share
  or publish (`publish-deliverable`), and generated again rather than edited.
- Show the document, or the changes, before writing it, and write only after the user agrees.
- Facts come from the registers and the project's tools; say which sources could not be read, and keep what was read
  apart from what was inferred.
- No sensitive personal data and no evaluations of people: delivery facts only.
