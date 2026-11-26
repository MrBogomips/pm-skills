---
name: wbs-builder
description: Builds and revises the work breakdown structure and its dictionary - the whole scope decomposed into deliverables and work packages, checked against the 100% rule, with acceptance and accountable role - from the charter or the roadmap; on request creates the work packages as work items. Use for "WBS", "work breakdown structure", "break down the scope".
---

# WBS builder

Decomposes the project's whole scope into deliverables and work packages, with a dictionary that says what each work
package contains and how it is accepted. The WBS is the scope reference for the RACI matrix, estimates and the
schedule.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **Project register**: `PROJECT.md`, declared in the project's `AGENTS.md` (or `CLAUDE.md`) as
  `- Project register: \`<path>\``: `Project name`, `Internal code`, `Deliverable language`, the `Delivery approach`,
  the naming Conventions and the Registers. With no project register, suggest `/pm-skills:project-setup`; you may
  still work in the session if the user wants, asking for what you would have read there and inventing no
  configuration.
- **Scope sources**: the latest project charter, else the product roadmap, else what the user gives; the latest
  release plan and the earlier WBS, found in the documents folder by the naming convention.
- **Registers, read only**: the RACI matrix (accountable roles, and the work packages it references), the tailoring
  register.
- **Tool capabilities** (through `TOOLS.md`): `issues`, to read the backlog's epics and, with `Mode: write`, to create
  work items.
- **Formats**: `${CLAUDE_PLUGIN_ROOT}/shared/documents/wbs.md` and `${CLAUDE_PLUGIN_ROOT}/shared/documents/common.md`.

## Steps

1. **Read the configuration** and the `## wbs-builder` section of `TAILORING.md`; say which rules apply. Say which
   scope source you will use and its version.
2. **Decompose** the scope into deliverables down to work packages: nouns, not activities, sized so that one role can
   be accountable for each. In an agile or hybrid project, keep the levels the backlog's epics already give and do
   not break work packages into stories.
3. **Check the 100% rule**: the children of each element cover all of it and nothing more; everything the scope
   source includes is somewhere, and its exclusions go under Out of scope. Where the sources do not detail an
   element, add no children to it: leave it a work package and say under it what is missing. Elements from approved
   changes are marked with the change ID.
4. **Dictionary**: for each work package its description, deliverable, acceptance and accountable role (from the
   RACI matrix when declared, else asked), shown as the table of the format, not summarized.
5. **Name and show.** Name the file with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/doc_naming.py" next --project <PROJECT.md> --dir <folder> --type wbs --date <today>`;
   for a revision, revise the existing WBS in place. Show the structure, the dictionary and the gaps; write it after
   the user agrees, with `status: draft` until they approve it, then `issued`.
6. **Revise.** When a revision renumbers, splits or removes a work package that `RACI.md` references, list the
   affected RACI rows and suggest `/pm-skills:raci-matrix`; the revision is major (`doc_naming.py bump <version> major`).
   A split changes what the kept ID means: the RACI rows on it are affected too.
7. **Work items**, only when the user asks and only through an `issues` tool with `Mode: write`: show the itemized
   list (title, type, parent, a link to the WBS) and create only those the user confirms on that list; add the item
   keys to the Work items column as a patch revision.
8. **Suggest the next steps**: `/pm-skills:estimate` for estimates by work package, `/pm-skills:schedule-check` for the
   activities and `/pm-skills:raci-matrix` for responsibilities. Report what you read, inferred and could not read.

## Always

- Cover the whole scope and nothing outside it; say where the 100% rule could not be checked.
- Keep IDs stable once the WBS is issued.
- Show before writing; write only after the user agrees.

## Never

- Never write to the registers from here: propose a handoff to the keeper (`${CLAUDE_PLUGIN_ROOT}/shared/handoff.md`)
  for what should go in `RACI.md`, `SCHEDULE.md` or any other register, and hand it over only when the user agrees.
  Follow-ups for the project manager may go to `/pm-skills:action-log`.
- Never create or change work items without a `Mode: write` tool and the user's confirmation on the itemized list.
- Never add scope the sources do not hold: an item the user wants that the scope source excludes is a change, so
  suggest `/pm-skills:change-request`.
- Never apply a tailoring rule that loosens a guardrail; say that it was ignored and why.

## Extension points

- `format`: headings or dictionary columns added or renamed, or a template.
- `rules`: extra checks, such as a maximum depth or a size limit for work packages.
- `steps`: extra steps before decomposing, before writing, or after creating work items.
- `terms`: the project's words for the WBS and its levels.
