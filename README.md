---
summary: Claude Code plugin for project managers that keeps a project's team register and suggests who should take a task or review a change.
---

# pm-skills

Project management skills for Claude Code. Keep a register of who is on the project, checked against GitHub and
Jira, and get suggestions, with reasons, for who should take a Jira task or review a pull request or a document.

## Why

Who is on a project, and who knows what, usually lives in someone's head or in a list nobody updates. This plugin
keeps that list in a small `TEAMS.md` in your project, checks it against the team's GitHub and Jira activity, and
uses it to suggest assignees and reviewers by area and recent work, leaving out authors and existing approvers.
The register holds project data only, and nothing is ever written to GitHub or Jira.

## Included components

| Skill | What it does |
|---|---|
| [`team-register`](skills/team-register/README.md) | Sets up, imports, updates and reconciles the team register. |
| [`assignment-advisor`](skills/assignment-advisor/README.md) | Suggests up to three people for a task or a review, with the reasons. |

Skills are grouped by PMBOK 8 performance domain; both belong to **Resources**.

## Agents

- `team-activity-scout`: collects each member's recent GitHub (or local git) and Jira activity for the two skills, read only.

## Hooks

- **SessionStart**: adds one line to the session's context with the register's size and last reconciliation, or a
  reminder when it is missing, invalid or not reconciled for over six weeks.
- **PostToolUse** (Write, Edit): when Claude edits the register, reports its validation errors back to Claude.

Both stay silent in projects that declare no register. They cannot be switched off one by one: disable the plugin to
stop them.

## Installation

```text
/plugin marketplace add MrBogomips/claude-plugins
/plugin install pm-skills@mrbogomips
```

**Standalone skills: no, plugin only.** The skills share the register format and validator inside the plugin, and
dispatch its agent.

## Quick start

In your project, ask Claude to "set up the team register" (or run `/pm-skills:team-register`). It imports an
existing team list if it finds one, or asks you who is on the team, confirms the GitHub repositories and Jira
projects to read, and shows you `TEAMS.md` and the line for `AGENTS.md` before writing them.

## Requirements

- Python 3, on macOS or Linux, for the validator and the hooks.
- For activity data: the `gh` CLI logged in and, for Jira, an Atlassian MCP server or the `acli` CLI. Without `gh`,
  commits are read from local clones of the repositories, with no pull requests or reviews. Each skill's README says
  what it can still do without them.

## Limitations

- Activity read from local clones is only as recent as their last fetch: the plugin never fetches.

## License

MIT
