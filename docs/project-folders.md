---
title: Project folders
area: plugin
type: concept
---

# Project folders

A project that uses the plugin follows a simple pattern: a short declaration, one configuration register, the
other registers, and documents placed where the project says. `/pm-skills:project-setup` builds it with you.

## The pieces

**The declaration.** The project's `AGENTS.md` (or `CLAUDE.md`) declares one line about the plugin and nothing else:

```markdown
- Project register: `PROJECT.md`
```

**The project register.** `PROJECT.md` holds the project's identity (client, name, codes, dates, contract type,
deliverable language), its profile (delivery approach, reporting cadence, sprint length), its naming conventions
and one line for each register in use. Every other skill reads it, so the registers can be anywhere: the paths it
lists, relative to the project root, are the truth.

**The other registers.** Each is a Markdown file kept by one skill (see [Registers and their
keepers](registers-and-keepers.md)). Without a better place, each goes at the project root.

**The Working documents section.** The project's `AGENTS.md` (or `CLAUDE.md`) has a Working documents section that
says where things go: documents in general or per type, the inbox, and where distribution formats such as Word or
PDF go. Skills read it before writing. When it is missing, a skill asks once and suggests recording the answer
there; `project-setup` proposes where documents go when the section is missing.

- **The inbox** is where incoming material lands. The default is `inbox/`. See [The inbox](inbox.md).
- **Distribution formats** (Word, PDF, slides) go where the section says, or next to their Markdown source when it
  says nothing. They are generated again from the Markdown, never edited.

## Naming and versioning

At setup you pick one of two naming presets for documents:

| Preset | Pattern | Example | Fits |
|---|---|---|---|
| By date | `<type>/<date>-<type>[-<slug>].md` | `status-report/2026-11-24-status-report.md` | internal projects |
| Coded | `<PROJ>-<CODE>-<NNN>[-<slug>].md` | `ACME-SR-007.md` | projects with an external client |

In the coded preset, `<PROJ>` is the project's internal code and `NNN` counts per document type. The type codes
have defaults (`SR` for a status report, `MM` for minutes, `MB` for a meeting brief) and a project may redefine
them. The name is computed by a script, never made up.

Every document has a `version` in its frontmatter. A revision changes the document in place and raises the version:
major for a change of content or structure, minor for compatible extensions and clarifications, patch for form and
formatting. Putting the version in the file name is an option, off by default. A distribution format keeps the base
name of its Markdown source.

## Everything under git

The project is under git, which keeps the history of every register and document. If it is not,
`project-setup` explains why it matters and proposes `git init`. That is why registers are plain Markdown, entries
are never deleted and a revision happens in place.

## Example: the Acme project

```text
acme-portal/
├── AGENTS.md                       declares PROJECT.md; Working documents section
├── PROJECT.md                      Acme Corp, ACME, coded naming, registers list
├── TOOLS.md                        Jira (read), GitHub (read), a renderer for docx
├── TEAMS.md                        ada-l, bo-k, cy-t
├── RISKS.md
├── DECISIONS.md
├── CHANGES.md
├── ACTIONS.md
├── inbox/                          incoming notes, transcripts, files
│   └── 2026-11-24-steering-notes.txt
└── docs/
    ├── ACME-MB-004.md              meeting brief
    ├── ACME-MM-004.md              meeting minutes
    └── ACME-SR-007.md              status report
```

The Working documents section of this project's `AGENTS.md` could read as follows. Its wording is the project's
own: the skills only need to find the folders in it.

```markdown
## Working documents

- Documents (status reports, briefs, minutes): `docs/`
- Inbox for incoming material: `inbox/`
- Word and PDF generated from documents: `docs/published/`
```
