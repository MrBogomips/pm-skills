---
name: backlog-refinement
description: Reviews the top of the product backlog from the issues tool - readiness of each item, proposed splits, a proposed order with reasons, stale and duplicate items - and writes back only through a write tool, on confirmation. The Product Owner decides. Use to refine or groom the backlog ("refine the backlog", "groom the backlog", "is the backlog ready"); not to plan a sprint.
---

# Backlog refinement

Checks whether the items at the top of the backlog are ready to be planned, proposes how to split the ones that are
too big and in what order to take them, and flags what has gone stale or is there twice. It proposes; ordering is
the Product Owner's decision.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **The project register**: `PROJECT.md`, declared by `` - Project register: `PROJECT.md` `` in the project's
  `AGENTS.md` (or `CLAUDE.md`): `Deliverable language`, the Profile keys `Delivery approach`, `Agile framework`,
  `Sprint length`, `Definition of Done`, `Definition of Workflow`, and the Registers. With no project register,
  suggest `/pm-skills:project-setup`; you may still work on items the user pastes, inventing no configuration.
- **Tool capabilities** (through `TOOLS.md`): `issues` for the backlog, its order, estimates, links and history;
  `code` and `releases` when an item's dependency or staleness depends on them.
- **Registers**, when declared: tailoring register, decision log, risk register, change log (`CHANGES.md`), the
  product roadmap document (to weigh items against its themes and horizons).
- **The scope**: which backlog or board, and how many items from the top (default: enough for the next two sprints,
  or the top 15 when there is no sprint length).

## Steps

1. **Read the configuration** and the `## backlog-refinement` section of `TAILORING.md`; say which rules you will
   apply. A `rules` entry may define the project's Definition of Ready; without one, check readiness against the
   criteria in step 3 and say that the project has no Definition of Ready.
2. **Read the backlog** through the `issues` tool: the items in scope in their current order, with description,
   acceptance criteria, estimate, labels, links, epic, status and the date of the last change. Read any item a top
   item links to. Say which tool and query you used and what you could not read. With no `issues` tool, work on the
   items the user pastes and suggest `/pm-skills:project-setup`.
3. **Check readiness** of each item: a clear outcome for a user or the client, testable acceptance criteria, a size
   that fits in a sprint (or in the Service Level Expectation for Kanban), known dependencies that are resolved or
   planned, and the Definition of Ready when there is one. Mark each `ready`, `nearly` (name the one thing missing)
   or `not ready` (name what is missing). Do not invent acceptance criteria: propose them as drafts to confirm.
4. **Propose splits** for items too big or mixing several outcomes: name the split you chose (by workflow step,
   business rule, data variation, interface, happy path first, spike then build) and why it fits this item, and give
   each part a title, an outcome and its acceptance criteria. Each part still delivers something usable.
5. **Propose an order** for the items in scope, each with its reason: value or theme of the roadmap, risk reduced
   (IDs from the risk register), dependency, cost of delay, a commitment (decision, approved change request,
   release). Show where it differs from the current order. It is a proposal for the Product Owner.
6. **Flag stale and duplicate items**: untouched for long (say how long and the date), made obsolete by a decision,
   a release or a change, or overlapping another item (say which and on what). Propose keep, merge, or close, with
   the reason; never close or merge on your own.
7. **Present** in the user's language: a table of the items with readiness and what is missing, then splits, the
   proposed order with reasons, stale and duplicates, and the sources read and not read. Keep what the tool shows
   apart from what you inferred.
8. **Write back**, only when the user asks and through an `issues` tool with `Mode: write`: each change (new item,
   edited description or criteria, reorder, label, link, close) shown exactly, one item at a time, or as an itemized
   batch the user confirms as a whole; make only the changes confirmed and report each one done or failed. With no
   `write` tool, give the proposals as text the user can apply.

## Always

- The order is the Product Owner's decision: present it as a proposal with reasons, and record whose decision it is.
- Name every source that could not be read and what the review cannot say because of it.
- Item keys and links come from the issues tool, never made up.
- Delivery facts only: no judgment of who wrote or owns an item.

## Never

- Never write to the issues tool without a `Mode: write` tool and the user's confirmation of each change or of the
  itemized batch.
- Never estimate on the team's behalf: an item without a size is marked as such; an estimate the user asks for is
  labelled as a proposal for the team.
- Never write to the registers from here: suggest `/pm-skills:risk-register`, `/pm-skills:decision-log` or
  `/pm-skills:change-request` for what they miss.

## Extension points

- `rules`: the project's Definition of Ready, and extra checks or approvals before a change is written back.
- `scale`: the size limit for a ready item and the age after which an item counts as stale.
- `steps`: extra steps before presenting or before writing back, such as a check against a client's backlog.
- `terms`: the project's words for backlog items, epics and readiness.
