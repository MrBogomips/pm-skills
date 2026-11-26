---
summary: For project managers - keeps ACTIONS.md, the log of actions with owner and due date, and shows the project manager's backlog by due date across the registers.
---

# action-log

Keeps `ACTIONS.md`, the project's action log. It records actions agreed in meetings, follow-ups and next steps,
each with an owner and a due date, links an action to the work item that carries it, and shows what the project
manager has to do: those actions together with the reviews, changes and gates that come due in the other registers.

## Why

Actions agreed in a meeting are forgotten in the minutes, and the project manager's own to-do is scattered across
risk reviews, stakeholder reviews, change requests and gates. This skill gives each action one home: what already
has a date and an owner in another register stays there and is never copied. The backlog is a view computed by a
script, so the order and the days left are never the model's guess. It asks for the owner and the date when they are
missing, and reads the state of a linked work item from the tool instead of trusting the row.

## Use cases

### Record the actions of a meeting

**Context:** The weekly call ended with three things to do and no one wrote them down.

**Action:** Paste the notes, or accept the actions that `/pm-skills:meeting-minutes` proposes, and ask "add these
actions".

**Result:** Each action with the next ID, an owner, a due date and its source, shown before writing; the ones that
already live in another register are named and skipped.

### See what you have to do

**Context:** Monday morning, and you want one list.

**Action:** Ask "what do I have to do this week?" or "PM backlog".

**Result:** A table sorted by due date with your open actions and the risk and stakeholder reviews, change requests
and gates that fall to you, each with its ID; overdue items first, and any register that could not be read named.

### Align an action with its ticket

**Context:** An action became a Jira item and the team has moved it.

**Action:** Ask "review the open actions".

**Result:** For each linked action the state read from the tool and a proposed change to the row (done, new owner or
date); the work item is never changed to match the log.

## Usage

Ask in your own words or run `/pm-skills:action-log`. Without an action log the skill starts by setting one up.

## Inputs and outputs

- Reads `PROJECT.md` (declared in `AGENTS.md` or `CLAUDE.md`), the `action-log` section of `TAILORING.md`, the team
  register, handoff proposals from other skills and, for the backlog, the risk, stakeholder, change and gate
  registers. With an `issues` tool it reads the state of linked work items.
- Writes `ACTIONS.md` in the format of [`shared/registers/actions.md`](../../shared/registers/actions.md), and once,
  with your consent, the `Action log` line in `PROJECT.md`. With an `issues` tool in write mode and your
  confirmation it creates a work item.
- Prints the backlog with `shared/scripts/pm_backlog.py`; never writes another register.

## Requirements

A project register (`/pm-skills:project-setup`). The backlog and the alignment with work items need the other
registers and an `issues` tool; the skill says what it could not read.

## Limitations

- Holds only actions with no other home; reviews, change requests, gate dates and delivery work stay where they are.
- Changes to risks, stakeholders, changes or gates go through their own skills.
- No contacts and no judgment of people in any entry.
