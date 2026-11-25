---
name: publish-deliverable
description: Renders a Markdown project document (status report, minutes, any deliverable) into Word, PDF, slides, email or an artifact through the renderer the project declares, and sends or uploads it only through a declared write tool. Use to export or distribute it ("export to Word", "make a PDF of the report", "publish the document"); not to write the document.
---

# Publish deliverable

Turns a Markdown deliverable into the format its readers need, with the renderer the project declares, and delivers
it only where and when the user says. The Markdown stays the source; the output is regenerated, never edited.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **The document**: a Markdown file with the common frontmatter (`type`, `status`, `version`), given by the user or
  the one just written in the session; and the format wanted.
- **The project register**: `PROJECT.md`, declared by `` - Project register: `PROJECT.md` `` in the project's
  `AGENTS.md` (or `CLAUDE.md`), for the Registers. With no project register, suggest `/pm-skills:project-setup`.
- **The tools register** `TOOLS.md`: renderers are tools with Purpose `publish` and Scope `<type> → <format>`
  (`status-report → docx`); delivery to an external system uses a tool in Mode `write` (`publish`, `documents`,
  `messages`). Format: `${CLAUDE_PLUGIN_ROOT}/shared/registers/tools.md`.
- **Documents**: `${CLAUDE_PLUGIN_ROOT}/shared/documents/common.md` (naming, where documents go).
- **Tailoring**: the `## publish-deliverable` section of `TAILORING.md`, when declared.

## Steps

1. **Read the configuration** and the tailoring section; say which rules you will apply.
2. **Check the source.** Read its frontmatter. When `status` is `draft`, or missing, say so and go on only if the
   user confirms publishing it as it is.
3. **Pick the renderer**: the `publish` tool whose Scope matches the document's `type` and the format. Several match:
   ask. None matches: go to step 4. Then go to step 5.
4. **Propose a renderer to reuse**, in this order, and say what each would produce:
   1. a skill already available in the session, from the user or the organization, including existing templates;
   2. an MCP server or a CLI on the `PATH` (pandoc for docx or PDF, for example);
   3. a script of the project, the user or the organization;
   4. for an artifact, an `artifact:<type>` renderer of the `pm-artifacts` plugin.

   Never build a new skill or script here; if nothing fits, suggest `/pm-skills:pm-tailoring` (planned) and stop.
   Show the `TOOLS.md` row for the chosen renderer (`| <name> | publish | <kind>:<target> | <type> → <format> | read |`,
   or `write` when it delivers outside the project), add it after the user agrees, and validate with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/tools_register.py" validate <path>` until it exits 0. With no tools
   register, render with the chosen renderer for this session only and suggest `/pm-skills:project-setup`.
5. **Place the output.** Keep the base name of the Markdown source with the format's extension
   (`ACME-SR-007.docx`), in the folder the project's Working documents section gives for distribution formats or
   published material, else next to the source; with no section, ask once and suggest recording it. An existing
   output of that name is regenerated, not edited: say it will be replaced.
6. **Render**, after the user agrees to the output path. Check the result opens and its content matches the source
   (headings, tables, version); report anything the renderer dropped.
7. **Deliver**, only when the user asks to send or upload it: through a tool in Mode `write` whose Scope covers the
   destination. Show exactly what goes where (recipients or location, subject, attachment) and send only after the
   user confirms; several destinations are confirmed on the itemized list. With no such tool, hand the file to the
   user and say it was not sent.
8. **Report** the renderer used, the output path, what was delivered and where, and anything that could not be done.

## Always

- The Markdown is the source of truth: to change the output, change the Markdown (through the skill that owns it),
  then render again.
- Render the document as it is: no content added, removed or reworded while publishing.
- Say which renderer and which tools were used, and which could not be reached.

## Never

- Never publish without the user asking to share or publish.
- Never send, upload or post anything outside the project without a tool in Mode `write` and the user's confirmation.
- Never write a secret or a contact into `TOOLS.md`.
- Never edit a generated file by hand.

## Extension points

- `rules`: extra checks or approvals, such as the project manager's approval before anything goes to the client.
- `steps`: extra steps before rendering or before delivering, such as a check of the cover page.
