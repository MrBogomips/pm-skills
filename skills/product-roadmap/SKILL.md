---
name: product-roadmap
description: Drafts and revises the product roadmap - Product Goal, themes, now/next/later or dated horizons - linked to epics in the issues tool and to releases, with what is committed kept apart from what is intended, versioned in place. Does not forecast dates. Use for "product roadmap", "update the roadmap", "roadmap di prodotto", "aggiorna la roadmap".
---

# Product roadmap

Writes and keeps the product roadmap: the Product Goal, the themes that serve it and the horizons in which they are
expected, every item tied to an epic or a release and marked committed or intended by its source.

## Inputs

- **The project register**: `PROJECT.md`, declared by `` - Project register: `PROJECT.md` `` in the project's
  `AGENTS.md` (or `CLAUDE.md`): `Project name`, `Internal code`, `Deliverable language`, the Profile keys
  `Delivery approach`, `Agile framework`, `Sprint length`, the naming Conventions and the Registers. With no project
  register, suggest `/pm-skills:project-setup`; you may still draft in the session if the user wants, asking for what
  you would have read there and inventing no configuration.
- **Tool capabilities** (through `TOOLS.md`): `issues` for epics, their status and links; `releases` for releases
  and their dates; `schedule` for committed milestones.
- **Registers**, when declared: tailoring register, decision log, change log (`CHANGES.md`), risk register.
- **Formats**: `${CLAUDE_PLUGIN_ROOT}/shared/documents/product-roadmap.md` and
  `${CLAUDE_PLUGIN_ROOT}/shared/documents/common.md`.
- **The previous roadmap**, when there is one, found in the documents folder by the naming convention (type
  `product-roadmap`, default code `RM`).

## Steps

1. **Read the configuration** and the `## product-roadmap` section of `TAILORING.md`; say which rules you will
   apply.
2. **Find the roadmap.** With an existing one, this is a revision: read it, and its `horizons` style. Without one,
   ask whether horizons are `now-next-later` or `dated`; propose `dated` only when the project commits dates to its
   horizons (a contract, a predictive or hybrid plan with milestones).
3. **Ask for what only the Product Owner sets**, when it is not in the previous roadmap or the user's request: the
   Product Goal, the themes, and the order within a horizon. Propose wording from the facts; never set them yourself.
4. **Gather the facts**: epics and their status from `issues`; releases, their status and dates from `releases`;
   milestones from `schedule`; decisions and approved change requests that commit scope or dates; risks and
   dependencies that bear on the horizons. Say which sources you read and which you could not.
5. **Classify** each item `committed` or `intended` by the format's rule, naming the source of each commitment.
   Match items to epics by key; an item with no epic says so, and an epic that serves no theme is listed for the
   user to place or leave out.
6. **Draft or revise** in the format, in the `Deliverable language`. On a revision, fill "Changes from the previous
   version" with what moved, was added or dropped, and why. When the user asks when something will be done, say
   that the roadmap does not forecast and that a forecast from throughput is the job of
   `/pm-skills:delivery-forecast` (planned).
7. **Name and show.** A new roadmap is named with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/doc_naming.py" next --project <PROJECT.md> --dir <folder> --type product-roadmap`
   in the folder the Working documents section gives (else ask once). A revision keeps its file and raises the
   version with `doc_naming.py bump <version> major|minor|patch` (major when the Product Goal or the themes change,
   minor when items move or are added, patch for form); with the version in the file name, it is a new file. Show
   the draft or the changes and the path; write only after the user agrees, with `status: draft`.
8. **Issue.** When the Product Owner approves, set `status: issued`. Suggest `/pm-skills:publish-deliverable` to
   share it, and `/pm-skills:backlog-refinement` when the roadmap changed the order of the work.

## Always

- Keep `committed` apart from `intended`, and name the source of every commitment.
- Keep the Product Goal, the themes and the order as the Product Owner set them; propose, do not decide.
- Name every source that could not be read and what the roadmap cannot say because of it.
- Show before writing; write only after the user agrees.

## Never

- Never compute, estimate or imply a date that the project has not committed.
- Never change epics or releases in the tools from here: suggest `/pm-skills:backlog-refinement` for the backlog.
- Never write to the registers: suggest `/pm-skills:decision-log` or `/pm-skills:change-request` for what they miss.

## Extension points

- `format`: sections added to or renamed in the roadmap, a project template, or the horizon names.
- `rules`: extra checks or approvals, such as the sponsor's approval before issuing.
- `steps`: extra steps before drafting or after issuing.
- `terms`: the project's words for the Product Goal, themes, epics and horizons.
