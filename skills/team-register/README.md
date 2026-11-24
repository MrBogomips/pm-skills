---
summary: For project managers - keeps TEAMS.md, the list of current and former team members with accounts, roles and areas, in step with GitHub and Jira.
---

# team-register

Keeps `TEAMS.md`, the register of who is on the project and who was, with GitHub and Jira accounts, roles and areas.
It imports an existing team list, records joins, departures and role changes, and reconciles the register with the
team's recent GitHub and Jira activity.

## Why

A team list goes stale quietly: people join through a pull request, leave without a note, change role. This skill
turns the list into a register with history, proposes the changes that GitHub and Jira activity suggest, and writes
only what you accept. The accounts, roles and areas it keeps are what `assignment-advisor` uses to suggest people.
It refuses personal data such as contacts or leave, so the register can live in a shared repository.

## Use cases

### Start from an informal team list

**Context:** Your project has a hand-written list of people, with emails and notes mixed in.

**Action:** Ask Claude to "set up the team register".

**Result:** A valid `TEAMS.md` with current and former members, a `- Team register:` line in `AGENTS.md`, and a
list of what was left out and why.

### Find out who joined or went quiet

**Context:** The register was last checked months ago.

**Action:** Ask Claude to "reconcile the team register".

**Result:** Numbered proposals (new people, inactive members, missing accounts); only the ones you accept are
written, and `Last reconciled` moves to today when every source could be read.

## Usage

Ask in your own words ("aggiorna il team", "Ada is the tech lead from today") or run `/pm-skills:team-register`.
Without a declared register the skill starts by setting one up.

## Inputs and outputs

- Reads and writes the register declared with `- Team register: \`<path>\`` in `AGENTS.md`, or in `CLAUDE.md` when
  `AGENTS.md` has no such line; by default `TEAMS.md` at the project root. The format is in
  [`shared/registers/teams.md`](../../shared/registers/teams.md).
- Writes nothing else, apart from the declaration line, which it adds once, with your consent.

## Requirements

For reconciliation, the `gh` CLI logged in and, for Jira, an Atlassian MCP server or the `acli` CLI. Without `gh`,
commits are read from local clones of the repositories: enough to find new people and missing commit emails, not to
call anyone inactive. When a source cannot be read, the skill says which one, proposes nothing that depends on it, and
leaves `Last reconciled` as it was. Setup and updates need neither.

## Limitations

- Holds project data only: no contacts, availability, allocation, appraisals or personal notes.
- Reads GitHub and Jira, never writes to them.
