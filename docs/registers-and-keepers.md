---
title: Registers and their keepers
area: plugin
type: concept
---

# Registers and their keepers

## Registers and documents

The plugin keeps two kinds of project material.

| | Register | Document |
|---|---|---|
| What it is | state that persists and that other skills or later sessions read again | a snapshot at a date |
| Examples | risks, decisions, actions, team | status report, meeting minutes, charter |
| Format | one schema per register, checked by a validator | common frontmatter and fixed headings per type |
| Changes | entries are updated in place, never deleted | revised in place with a new `version` |

There is one register per type: the plugin does not mix risks, issues and decisions in a single log.

## The registers and who keeps them

Every register has exactly one keeper: the skill that alone writes it. The file names below are the usual ones; the
project register says where each register is in your project.

| Register | File | Keeper |
|---|---|---|
| Project register | `PROJECT.md` | `project-setup` |
| Tools register | `TOOLS.md` | `project-setup` |
| Tailoring register | `TAILORING.md` | `pm-tailoring` |
| Team register | `TEAMS.md` | `team-register` |
| Capacity register | `CAPACITY.md` | `capacity-register` |
| Stakeholder register | `STAKEHOLDERS.md` | `stakeholder-register` |
| RACI matrix | `RACI.md` | `raci-matrix` |
| Decision log | `DECISIONS.md` | `decision-log` |
| Risk register | `RISKS.md` | `risk-register` |
| Change log | `CHANGES.md` | `change-request` |
| Gate register | `GATES.md` | `phase-gate-review` |
| Schedule register | `SCHEDULE.md` | `schedule-check` |
| Budget register | `BUDGET.md` | `budget-tracker` |
| Action log | `ACTIONS.md` | `action-log` |

Flow snapshots are data files, not registers: the skills that compute them write them.

## The handoff

When a skill finds something another register should hold (a decision in a meeting, a risk in a charter, a change
request in a transcript, a follow-up for you), it does not write it. It prepares a **handoff proposal** for the
keeper. Everything else in the plugin composes through shared files; this is the only time one skill runs another.

A proposal looks like this:

```markdown
1. **Handoff to `/pm-skills:decision-log`**: add a decision
   - Register: `DECISIONS.md`
   - Source: `docs/ACME-MM-004-steering.md`
   - Raised by: `meeting-minutes`
   - Fields:
     - Date: 2026-11-24
     - Decided by: sponsor
     - Decision: Move the go-live of release 2.0 to 2027-01-15.
```

The flow:

1. The skill shows its proposals, numbered, and asks which to hand off. You can accept all, some or none.
2. For each accepted one it says it is handing off to the keeper and runs that skill with the proposals, one keeper
   at a time. `project-setup` and `pm-tailoring` only start when you run them yourself: for those, the skill prints
   the proposals with the `/pm-skills:<keeper>` command ready to paste.
3. The keeper treats a proposal as input, not an order: it applies its own rules, asks for what is missing, shows
   you the change, writes it once you agree and validates the register. Accepting a proposal in step 1 is not
   agreement to the write: the keeper always shows the change first.
4. The keeper reports the IDs it assigned (such as `D-004`), and the first skill records them where it links to
   them, for example in the minutes.

A new entry carries no ID in the proposal: the keeper computes it just before writing. A value the proposing skill
inferred is marked `(inferred)`; a field it could not fill is left out, and the keeper asks you for it.

A declined proposal is not recorded as a register entry. Some documents have a place for it as a note.

Even if you ask, a skill will not write a register it does not keep: it hands off instead.

## One register, one declaration

`PROJECT.md` lists the registers the project uses, one line each. When a keeper creates its register, it adds that
line, and nothing else, to `PROJECT.md`; this is the one case where a skill other than `project-setup` touches
that file. The validator then checks the result.

## One home per action

Something to do lives in one place only. The action log holds the actions that have no other home. A risk review,
a change request to assess, a gate date or a piece of delivery work stays in its own register or tool, and your
PM backlog is a view over all of them. See [Actions and the PM backlog](actions-and-backlog.md).

## Checks

Two hooks keep registers valid, quietly:

- at the start of a session, one line sums up the registers the project declares, or reminds you that one is missing
  or invalid;
- when Claude edits a declared register, validation errors are reported back at once.

Both stay silent in a project that declares no project register, except for a one-line reminder when a pre-1.0
team register is still declared in the instruction file.

For a wider check, the `register-reviewer` agent reads the declared registers and checks them against each other
(owners against the team register, decision and change references, gates against the schedule, overdue items) and,
when given facts collected from your tools, against the real state of the project. It only reads: it reports ranked
findings and names the keeper that should fix each one.
