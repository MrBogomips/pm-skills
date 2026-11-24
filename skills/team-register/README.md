---
summary: For project managers - keeps TEAMS.md, the list of current and former team members with accounts, roles and areas, in step with the project's tools.
---

# team-register

Keeps `TEAMS.md`, the register of who is on the project and who was, with GitHub and Jira accounts, roles and areas.
It imports an existing team list, records joins, departures and role changes, and reconciles the register with the
team's recent activity in the project's code and issue tools (GitHub, Jira or others declared in `TOOLS.md`).

## Why

A team list goes stale quietly: people join through a pull request, leave without a note, change role. This skill
turns the list into a register with history, proposes the changes that recent activity suggests, and writes only
what you accept. The accounts, roles and areas it keeps are what `assignment-advisor` uses to suggest people.
It refuses sensitive personal data and evaluations, so the register can live in a shared repository.

## Use cases

### Start from an informal team list

**Context:** Your project has a hand-written list of people, with emails and notes mixed in.

**Action:** Ask "set up the team register".

**Result:** A valid `TEAMS.md` with current and former members, a `- Team register:` line in the Registers section
of `PROJECT.md`, and a list of what was left out and why.

### Find out who joined or went quiet

**Context:** The register was last checked months ago.

**Action:** Ask "reconcile the team register".

**Result:** Numbered proposals (new people, inactive members, missing accounts); only the ones you accept are
written, and `Last reconciled` moves to today when every source could be read.

## Usage

Ask in your own words ("aggiorna il team", "Ada is the tech lead from today") or run `/pm-skills:team-register`.
Without a declared register the skill starts by setting one up.

## Inputs and outputs

- Reads and writes the register declared with `- Team register: \`<path>\`` in the Registers section of
  `PROJECT.md`; by default `TEAMS.md` at the project root. The format is in
  [`shared/registers/teams.md`](../../shared/registers/teams.md).
- Reads the project's `code` and `issues` tools through the `project-activity-scout` agent.
- Writes nothing else, apart from the declaration line, which it adds once, with your consent.

## Requirements

A project register (`/pm-skills:project-setup`). For reconciliation, a tools register with the project's `code` and
`issues` tools, for example GitHub through the `gh` CLI and Jira through an Atlassian MCP server. When the code host
cannot be reached, commits are read from local clones: enough to find new people and missing commit emails, not to
call anyone inactive. When a tool cannot be read, the skill says which one, proposes nothing that depends on it, and
leaves `Last reconciled` as it was. Setup and updates need no tool.

## Limitations

- Holds delivery facts only: no contacts, availability, allocation, appraisals or personal notes.
- Reads the project's tools, never writes to them.
