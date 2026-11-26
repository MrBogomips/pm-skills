---
summary: For project managers - renders a Markdown deliverable into Word, PDF, slides, email or an artifact with the renderer the project declares, and sends it only through a declared write tool after confirmation.
---

# publish-deliverable

Turns a Markdown deliverable (a status report, minutes, a charter) into the distribution format its readers need,
through the renderer declared in the project's tools register, and delivers it only when and where you say.

## Why

Deliverables live as Markdown under git; readers want Word, PDF or an email. Hand-made conversions drift from the
source and get edited on their own. This skill uses one declared renderer per document type and format, keeps the
source's name, regenerates instead of editing, refuses drafts unless you confirm, and sends nothing outside the
project without a write tool and your agreement. When the project has no renderer yet, it proposes one to reuse and
hands the row to the skill that keeps `TOOLS.md`. Minutes lose their `Internal notes` section before they are rendered or sent.

## Use cases

### Export the status report to Word

**Context:** `ACME-SR-007.md` is issued; `TOOLS.md` declares a Word renderer for `status-report → docx`.

**Action:** Ask "export the status report to Word".

**Result:** `ACME-SR-007.docx` in the published-material folder, rendered by the declared tool, with a check that the
content matches the source.

### First PDF, no renderer yet

**Context:** The minutes have to go out as PDF and no `publish` tool covers them.

**Action:** Ask "make a PDF of the minutes".

**Result:** A proposed renderer to reuse (a session skill, pandoc, a project script), the `TOOLS.md` row to add, and
the PDF once you agree.

## Usage

Ask in your own words ("export to Word", "make a PDF", "publish the document") or run
`/pm-skills:publish-deliverable` with the document's path and the format.

## Inputs and outputs

- Reads the Markdown document and its frontmatter, `PROJECT.md`, `TOOLS.md` and the `publish-deliverable` section of
  `TAILORING.md`.
- Writes the rendered file, with the source's base name, where the project's Working documents section says.
- May hand a renderer row to `/pm-skills:project-setup`, which keeps `TOOLS.md`, with your agreement.
- Always removes a section headed `Internal notes` (`Note interne`) from minutes in what it renders or sends, and says so; the Markdown source keeps it.
- Sends or uploads only through a tool in Mode `write`, after you confirm what goes where.

## Requirements

A renderer reachable in the session: a skill, an MCP server, a CLI such as pandoc, a script, or an artifact renderer
of the `pm-artifacts` plugin. A tools register is recommended (`/pm-skills:project-setup`).

## Limitations

- Does not build renderers: for a project-specific one, see `/pm-skills:pm-tailoring` (planned).
- Does not change content: fix the Markdown and render again.
