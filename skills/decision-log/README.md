---
summary: For project managers - keeps DECISIONS.md, the log of decisions with their context, options and who took them, and answers what was decided and why.
---

# decision-log

Keeps `DECISIONS.md`, the project's decision log. It records decisions with their context, the options considered
and who took them, replaces or withdraws them without rewriting history, and answers questions such as "why did we
pick the message broker?".

## Why

Decisions get lost in meetings and threads, and months later nobody remembers why the team chose what it chose, or
whether the choice still holds. This skill asks only for what is missing, refuses to record a discussion as a
decision, links a decision to the one it replaces, and points out the consequences that should go in the risk
register.

## Use cases

### Record a decision from a meeting

**Context:** The steering committee chose a managed message broker; the minutes have the reasons.

**Action:** Ask "record the decision on the message broker from today's minutes".

**Result:** A new entry with the next ID, context, options, decision and source, shown before writing; if it
replaces an earlier decision, both entries are linked in the same write.

### Find out why

**Context:** A new developer asks why notifications do not use the jobs table.

**Action:** Ask "what did we decide about notifications?".

**Result:** The decision in force, with its ID, date, who decided and why, and the earlier decision it replaced.

### Keep a discussion out of the log

**Context:** You paste a thread where the team leaned towards a new framework but nobody decided.

**Action:** Ask "record a decision".

**Result:** The skill says the thread holds no decision, records nothing, and offers to record it once someone
decides.

## Usage

Ask in your own words or run `/pm-skills:decision-log`. Without a decision log the skill starts by setting one up.

## Inputs and outputs

- Reads `PROJECT.md` (declared in `AGENTS.md` or `CLAUDE.md`), the `decision-log` section of `TAILORING.md`, the
  team register, and, when you point to one, a source through the project's tools (meetings, messages, documents,
  issues).
- Writes `DECISIONS.md` in the format of [`shared/registers/decisions.md`](../../shared/registers/decisions.md),
  and once, with your consent, the `Decision log` line in `PROJECT.md`.
- Hands risks to `/pm-skills:risk-register` as proposals; never writes the risk register.
- Takes changes handed off by other skills (for example from meeting minutes), checks them against its own rules, and reports the IDs it assigned.

## Requirements

A project register (`/pm-skills:project-setup`). No tool is required.

## Limitations

- Records decisions taken, not proposals or open questions.
- An accepted decision is never edited beyond a fix of form: a change of mind is a new decision.
- No contacts and no judgment of people in any entry.
