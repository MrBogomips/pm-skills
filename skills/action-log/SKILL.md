---
name: action-log
description: Keeps the action log (ACTIONS.md) - actions, follow-ups and next steps with owner and due date, linked to work items - and shows the project manager's backlog, sorted by due date, across the registers. Use for "PM backlog", "my to-do", "what do I have to do", "open actions", "action items", "follow-ups", "add an action".
---

# Action log

Keeps `ACTIONS.md`: the actions that have no other home, each with an owner and a due date, and shows the project
manager's backlog: those actions plus what the other registers say is due, by date. It writes only the log.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **Project register**: `PROJECT.md`, declared in the project's `AGENTS.md` (or `CLAUDE.md`) as
  `- Project register: \`<path>\``. The log is its `- Action log: \`<path>\`` line under Registers. With no project
  register, suggest `/pm-skills:project-setup`; if the user wants to go on in the session, work on a path they name
  and invent no configuration.
- **Format**: `${CLAUDE_PLUGIN_ROOT}/shared/registers/actions.md`, the single source for keys, statuses, rules and
  what does not belong in the log. Read it before writing; do not restate it to the user.
- **Tailoring**: the `## action-log` section of the tailoring register, when declared.
- **Handoff proposals** from other skills (minutes, meeting preparation, inbox triage, status reports), per
  `${CLAUDE_PLUGIN_ROOT}/shared/handoff.md`: input to check, not an order.
- **Team register**, read only: slugs for `Owner` and `Raised by`.
- **Other registers, read only**, through the backlog script: risks, stakeholders, changes, gates.
- **Tools** (from the tools register, by capability): `issues`, to read the state of a linked work item and, only
  with Mode `write` and the user's confirmation, to create one. Without it, say the state could not be read.

## Steps

1. **Start.** Read the project register, the log and the tailoring section. Say which tailoring rules apply.
2. **Set up** (no log, or the user asks): propose `ACTIONS.md` at the project root (or where the Working documents
   section places registers) with the title only, and the line `- Action log: \`ACTIONS.md\`` for the Registers
   section of `PROJECT.md`. Show both, write after the user agrees, then validate `PROJECT.md`:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/project_register.py" validate <path>`.
3. **Add an action** from the user's words, a handoff proposal or a source they point to.
   - Ask only for what is missing among Owner, Due and Action; Source is where it came from, Raised the day it was
     agreed or received. "We" or "someone" is not an owner: ask. A date such as "next week" is turned into a day
     and shown for confirmation.
   - **One home.** If it already has a date and an owner elsewhere, do not record it: a risk or stakeholder review,
     a change request to assess or implement, a gate date or condition, delivery work (issues tool, schedule), a
     retrospective action. Say where it lives and, if that entry is missing or wrong, point to its keeper
     (`/pm-skills:risk-register`, `stakeholder-register`, `change-request`, `phase-gate-review`) and write nothing.
   - Look for an open action with the same owner and subject first; a duplicate is pointed out, not added.
   - The ID is the highest `AC-` number in the file plus one, never reused; Status `open`. A handoff may carry
     several actions: show them all, record those the user accepts and report the assigned IDs back to the proposer.
4. **Link a work item.** When the action becomes delivery work, and only if the user asks: with an `issues` tool in
   Mode `write`, propose the item (title, description, assignee from the team register) and create it after the
   user confirms; then record `Tool` (as named in the tools register) and `Item` on the action. If the item exists,
   record the pair. Without a write tool, say so and give the text to create the item by hand.
5. **Review and align.** For open actions with `Tool` and `Item`, read the item's state through `issues` and
   compare: the tool is the source of truth. Propose the change to the row (`done` with `Closed` and an `Outcome`,
   a new `Due` or `Owner` the tool shows) with what was read; write only what the user accepts. Never change the work
   item to match the row.
6. **Close or drop.** `done` with `Closed` (and `Outcome` when something is worth keeping), or `dropped` with the
   reason in `Outcome`. Never delete a row. A new `Due` or `Owner` is shown and agreed first.
7. **The backlog** ("PM backlog", "my to-do", "what do I have to do", "open actions"). Run, with the owner the user
   means (default the project manager) and a horizon if asked:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/pm_backlog.py" <path to PROJECT.md> [--owner NAME] [--days N]`
   and present the table as printed: do not reorder it, recompute days or add rows. Group by what is overdue, due
   this week and later or undated when the user wants a summary. Name what the script could not read. For an item
   that is not an `AC-` action, say which skill keeps it (`R-` risk-register, `S-` stakeholder-register, `CR-`
   change-request, `G-` phase-gate-review): offer to run it, never edit that register from here.
8. **Validate** after every write, fixing until it exits 0:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/actions_register.py" validate <path>`.

## Always

- **Show before writing**: every change to `ACTIONS.md` or its declaration line in `PROJECT.md` is shown first and
  written after the user agrees; one write per change.
- **Facts apart from inferences**: say what was taken from the source, what was inferred (owners, dates) and which
  sources could not be read.
- **People**: owners as slugs or roles; no contacts and no judgment of a person in any entry.
- Talk and write values in the user's language, or the project's `Deliverable language`; keys stay in English.

## Never

- Never copy into the log what another register holds, and never write another register: hand off to its keeper.
- Never compute a date, a count or an order yourself in the backlog: the script does.
- Never create or change a work item without an `issues` tool in Mode `write` and the user's confirmation.
- Never delete an action or reuse an ID; never mark an action done on the strength of silence.
- Never apply a tailoring rule that loosens a guardrail; say that it was ignored and why.

## Extension points

- `rules`: extra checks, for example a due date required within a number of days, or who may own an action.
- `steps`: extra steps when adding an action, for example linking the ticket that tracks it.
- `terms`: the project's words for actions, follow-ups and the backlog in conversation.
