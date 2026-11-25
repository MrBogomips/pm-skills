---
summary: Claude Code plugin for project managers, optimized for software: skills that keep small validated registers under git and draft the recurring project documents from them.
---

# pm-skills

Project management skills for Claude Code. Your project keeps small Markdown registers under git; the skills read them
with your issue tracker and code host, draft the recurring documents, compute metrics, forecasts and earned value with
tested scripts, and suggest who should take or review work. Optimized for software, usable on any project.

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
| [`actionable-message`](skills/actionable-message/README.md) | Stakeholders | Emails and chat messages where every request has an owner, a deadline, references and a contact. |
| [`change-request`](skills/change-request/README.md) | Governance, Scope, Finance | Raises change requests in `CHANGES.md`, assesses their impact, records the decision. |
| [`stakeholder-register`](skills/stakeholder-register/README.md) | Stakeholders | Keeps `STAKEHOLDERS.md`: roles, interest, influence and engagement, with the approach. |
| [`capacity-register`](skills/capacity-register/README.md) | Resources | Keeps `CAPACITY.md`: calendar, allocation and absences; computes available person-days. |
| [`sprint-planning`](skills/sprint-planning/README.md) | Scope, Schedule | The sprint plan: Sprint Goal and selection against capacity and recent throughput. |
| [`sprint-review`](skills/sprint-review/README.md) | Scope, Stakeholders | What was delivered against the Sprint Goal, feedback and backlog adaptations. |
| [`retrospective`](skills/retrospective/README.md) | Governance | Prepares and records a retrospective with owned actions, following up the previous ones. |
| [`backlog-refinement`](skills/backlog-refinement/README.md) | Scope | Readiness, splitting and ordering proposals for the top of the backlog. |
| [`product-roadmap`](skills/product-roadmap/README.md) | Governance, Scope | The product roadmap: Product Goal, themes and horizons, committed versus intended. |
| [`flow-metrics`](skills/flow-metrics/README.md) | Schedule, Scope | Cycle time, throughput, WIP and work item age from a saved flow snapshot, team-level; DORA when the tools allow. |
| [`delivery-forecast`](skills/delivery-forecast/README.md) | Schedule | When N items will be done, or how many by a date: Monte Carlo percentiles, never a single date. |
| [`release-plan`](skills/release-plan/README.md) | Scope, Schedule | Scope and dates of a release from the forecast, the roadmap and approved changes. |
| [`estimate`](skills/estimate/README.md) | Finance, Schedule | Three-point and analogous estimates of effort and cost, from the rates per role in `BUDGET.md`. |
| [`schedule-check`](skills/schedule-check/README.md) | Schedule | Critical path, float and slip against the baseline; keeps `SCHEDULE.md` and its baselines. |
| [`budget-tracker`](skills/budget-tracker/README.md) | Finance | Keeps `BUDGET.md`; earned value, reserves apart, forecasts at completion. |
| [`project-charter`](skills/project-charter/README.md) | Governance, Scope | The project charter from the registers, critically reviewed; seeds the risk, stakeholder and gate registers. |
| [`wbs-builder`](skills/wbs-builder/README.md) | Scope | The work breakdown structure and its dictionary, checked against the 100% rule; work packages as work items on request. |
| [`raci-matrix`](skills/raci-matrix/README.md) | Resources | Keeps `RACI.md`: responsibilities by role, exactly one accountable per deliverable. |
| [`communication-plan`](skills/communication-plan/README.md) | Stakeholders | Who receives what, when and through which channel, from the stakeholder register and the RACI matrix. |
| [`phase-gate-review`](skills/phase-gate-review/README.md) | Governance | Keeps `GATES.md`; assesses a gate's criteria against evidence and records the outcome once decided. |
| [`lessons-learned`](skills/lessons-learned/README.md) | Governance | What a project or phase learned, from its retrospectives, gates, decisions and changes, never about people. |
| [`team-charter`](skills/team-charter/README.md) | Resources | Prepares the team charter workshop and records the agreements the team made. |
| [`pm-tailoring`](skills/pm-tailoring/README.md) | All | Adapts the plugin to the project with the lightest change that works. User-invocable only. |
| [`pm-coach`](skills/pm-coach/README.md) | All | Reasoned advice grounded in your registers. User-invocable only. |

Domains are the performance domains of the PMBOK Guide, Eighth Edition. Agile skills follow the Scrum Guide 2020
and the Kanban Guide; more are planned (see `DESIGN.md`).

## Agents

- `project-activity-scout`: collects recent activity from the project's tools, per person or per project,
  read only.
- `pm-critical-reviewer`: challenges risk responses, change impact analyses, estimates, charters, gate
  assessments and deliverables before they go out, read only.
- `flow-data-scout`: collects the transition history of work items from the issues tool as a flow snapshot,
  with no assignees, read only.

## Hooks

- **SessionStart**: adds one line to the session's context summing up the registers the project declares, or a reminder when one is missing or invalid.
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
2. Ask to "set up the team register", then use the skills in your own words: "add a risk", "write the minutes",
   "status report", "plan the next sprint", "who should review acme/web#42?". Ask in any language: the skills answer in it, and in
   Italian they use the terms of a shared glossary (`shared/glossary/it.md`).
3. To adapt a skill to your project's way of working, run `/pm-skills:pm-tailoring`.

### Upgrading from 0.x

Version 1.0 declares registers in `PROJECT.md` instead of `AGENTS.md`, moves the team register's `Sources:` line to
`TOOLS.md`, and renames the `team-activity-scout` agent to `project-activity-scout`. At the first session the hook
reminds you; run `/pm-skills:project-setup` and it proposes the migration in one step.

## Requirements

- Python 3, on macOS or Linux, for the validators, the scripts and the hooks; git for the project.
- For facts from your tools: the ones you declare in `TOOLS.md`, for example the `gh` CLI logged in for GitHub and an
  Atlassian MCP server for Jira. Without a code host CLI, commits are read from local clones. Skills say in their
  output which sources they could not read.

## Limitations

- Activity read from local clones is only as recent as their last fetch: the plugin never fetches.
- Numbers come from registers, tools and scripts; skills do not estimate figures while writing.

## License

MIT
