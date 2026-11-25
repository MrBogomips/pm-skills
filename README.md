---
summary: Claude Code plugin for project managers, optimized for software projects - configuration, team, capacity, stakeholders, risks, decisions, change requests, Scrum events, roadmap, status reports, publishing, tailoring and a coach, grounded in small validated registers under git.
---

# pm-skills

Project management skills for Claude Code. Your project keeps a few small Markdown registers under git (its
configuration, tools, team, capacity, stakeholders, risks, decisions and change requests); the skills read them
together with your issue tracker and code host, draft the recurring documents (minutes, status reports, sprint
plans, reviews, retrospectives, the roadmap), and suggest who should take or review work. They work
on any project and are optimized for building software and managing software products.

## Why

Project management work is spread across heads, tickets and documents nobody updates. This plugin keeps the state
that matters in validated registers next to the project, reads facts from the tools you already use, says which
sources it could not read, and keeps you in charge: every write is shown first, nothing goes to an external system
unless you declared that tool writable and confirmed the change, and no register holds sensitive personal data or
evaluations of people.

## Included components

| Skill | Domain | What it does |
|---|---|---|
| [`project-setup`](skills/project-setup/README.md) | Governance | Sets up and reviews `PROJECT.md` and `TOOLS.md`; migrates projects from 0.x. User-invocable only. |
| [`team-register`](skills/team-register/README.md) | Resources | Keeps `TEAMS.md` and reconciles it with recent activity. |
| [`assignment-advisor`](skills/assignment-advisor/README.md) | Resources | Suggests up to three people for a task or a review, with the reasons. |
| [`risk-register`](skills/risk-register/README.md) | Risk | Identifies, assesses, plans responses to and reviews risks in `RISKS.md`. |
| [`decision-log`](skills/decision-log/README.md) | Governance | Records decisions in `DECISIONS.md` and answers what was decided and why. |
| [`meeting-minutes`](skills/meeting-minutes/README.md) | Stakeholders | Minutes with decisions, actions and risks, proposed for the registers. |
| [`status-report`](skills/status-report/README.md) | Governance, Stakeholders | The status report for the reporting period, outcomes first. |
| [`publish-deliverable`](skills/publish-deliverable/README.md) | Stakeholders | Renders a Markdown deliverable into Word, PDF, slides, email or an artifact. |
| [`change-request`](skills/change-request/README.md) | Governance, Scope, Finance | Raises change requests in `CHANGES.md`, assesses their impact, records the decision. |
| [`stakeholder-register`](skills/stakeholder-register/README.md) | Stakeholders | Keeps `STAKEHOLDERS.md`: roles, interest, influence and engagement, with the approach. |
| [`capacity-register`](skills/capacity-register/README.md) | Resources | Keeps `CAPACITY.md`: calendar, allocation and absences; computes available person-days. |
| [`sprint-planning`](skills/sprint-planning/README.md) | Scope, Schedule | The sprint plan: Sprint Goal and selection against capacity and recent throughput. |
| [`sprint-review`](skills/sprint-review/README.md) | Scope, Stakeholders | What was delivered against the Sprint Goal, feedback and backlog adaptations. |
| [`retrospective`](skills/retrospective/README.md) | Governance | Prepares and records a retrospective with owned actions, following up the previous ones. |
| [`backlog-refinement`](skills/backlog-refinement/README.md) | Scope | Readiness, splitting and ordering proposals for the top of the backlog. |
| [`product-roadmap`](skills/product-roadmap/README.md) | Governance, Scope | The product roadmap: Product Goal, themes and horizons, committed versus intended. |
| [`pm-tailoring`](skills/pm-tailoring/README.md) | All | Adapts the plugin to the project with the lightest change that works. User-invocable only. |
| [`pm-coach`](skills/pm-coach/README.md) | All | Reasoned advice grounded in your registers. User-invocable only. |

Domains are the performance domains of the PMBOK Guide, Eighth Edition. Agile skills follow the Scrum Guide 2020
and the Kanban Guide; more are planned (see `DESIGN.md`).

## Agents

- `project-activity-scout` (`haiku`): collects recent activity from the project's tools, per person or per project,
  read only.
- `pm-critical-reviewer` (`opus`): challenges risk responses, change impact analyses and deliverables before they go
  out, read only.

## Hooks

- **SessionStart**: adds one line to the session's context summing up every register the project declares (size,
  last review, risks past their review date), or a reminder when one is missing or invalid.
- **PostToolUse** (Write, Edit): when Claude edits a declared register, reports its validation errors back.

Both stay silent in projects that declare no project register. They cannot be switched off one by one: disable the
plugin to stop them.

## Installation

```text
/plugin marketplace add MrBogomips/claude-plugins
/plugin install pm-skills@mrbogomips
```

**Standalone skills: no, plugin only.** The skills share register formats, validators and scripts inside the
plugin, and dispatch its agents.

## Quick start

1. In your project, run `/pm-skills:project-setup`. It proposes `PROJECT.md` (identity, profile, naming conventions)
   and `TOOLS.md` (for example Jira and GitHub, read only) from what it finds, and writes them after you agree.
2. Ask to "set up the team register", then use the skills in your own words: "add a risk", "scrivi il verbale della
   riunione", "status report", "pianifica lo sprint", "who should review acme/web#42?".
3. To adapt a skill to your project's way of working, run `/pm-skills:pm-tailoring`.

### Upgrading from 0.x

Version 1.0 declares registers in `PROJECT.md` instead of `AGENTS.md`, moves the team register's `Sources:` line to
`TOOLS.md`, and renames the `team-activity-scout` agent to `project-activity-scout`. At the first session the hook
reminds you; run `/pm-skills:project-setup` and it proposes the migration in one step.

## Requirements

- Python 3, on macOS or Linux, for the validators, the scripts and the hooks; git for the project.
- For facts from your tools: the ones you declare in `TOOLS.md`, for example the `gh` CLI logged in for GitHub and an
  Atlassian MCP server for Jira. Without a code host CLI, commits are read from local clones. Each skill's README says
  what it can still do without them.

## Limitations

- Activity read from local clones is only as recent as their last fetch: the plugin never fetches.
- Numbers come from registers, tools and scripts; skills do not estimate figures while writing.

## License

MIT
