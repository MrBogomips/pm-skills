---
title: Actions and the PM backlog
area: governance
type: operational
---

# Actions and the PM backlog

`action-log` keeps the action log, `ACTIONS.md`, and shows your backlog: your open actions plus what the other
registers say is due, by date.

## What goes in the log

The log holds the actions that have no other home:

- actions agreed in a meeting;
- follow-ups;
- next steps a skill recommends to you;
- requests you received.

Each action has an owner (a team register slug such as `ada-l`, or a role such as `Project manager`), a due date, a
source and a status: `open`, `done` or `dropped`. "We" or "someone" is not an owner: the skill asks. A date like
"next week" is turned into a day and shown for your confirmation. An action is never deleted; one that is no longer
needed is dropped, with the reason. Actions state facts and work, never a judgment of a person.

## What stays elsewhere

Something to do lives in one place only. These stay where they are and are not copied into the log:

| What | Where it lives |
|---|---|
| risk reviews | the risk register |
| stakeholder reviews | the stakeholder register |
| change requests to assess or implement | the change log |
| gate dates and conditions | the gate register |
| delivery work | the issues tool, or the schedule register |
| retrospective actions | the retrospective document |

If you ask to add something that already has a date and an owner elsewhere, the skill says where it lives and, if
that entry is missing or wrong, points to its keeper.

## Linking a work item

When an action becomes delivery work, you can ask for a work item. With an `issues` tool declared `write` in
`TOOLS.md`, the skill proposes the item and creates it only after you confirm; then the action records the tool
and the item key. If the item already exists, you can record the pair. Without a write tool, the skill gives you
the text to create the item by hand.

From then on the tool holds the state of the work. When you review, the skill reads the item's state through the
`issues` capability and proposes to align the row (done, a new due date or owner). It never changes the work item to
match the row.

## The PM backlog

Ask "PM backlog", "my to-do" or "what do I have to do". The skill runs a script and presents its table as printed:
due date, days from today (negative when overdue), origin, owner and what. The skill does not reorder it or
recompute the days.

It lists:

- the open actions of the owner (by default the project manager; you can ask for another owner or everyone);
- the live risks and active stakeholders the owner reviews;
- for the project manager's view and for everyone: the change requests to assess or implement, the open gates with
  a planned date, and the conditions of gates passed with conditions.

You can ask for a horizon, such as the next 7 days: it keeps what is due within it, the overdue and the undated.
A register that is missing or invalid is named after the table. For an item that is not an action, the skill says
which skill keeps it and offers to run it; it never edits that register from the backlog.

## How other skills feed it

Skills that find something for you to do hand it to `action-log` as a proposal: `meeting-minutes` (actions from the
meeting), `meeting-prep` (preparation tasks), `inbox-triage` (a request for the project manager), `change-request`
(follow-ups) and others. The skill checks each proposal, looks for an open duplicate, asks for what is missing,
shows you the action and writes it once you agree; it then reports the IDs (`AC-021`) back. See
[Registers and their keepers](registers-and-keepers.md).
