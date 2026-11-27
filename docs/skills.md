---
title: Skills
area: plugin
type: operational
---

# Skills

Every skill is a job you ask for in your own words, or start with `/pm-skills:<name>`. Three are started on purpose
only and Claude does not pick them on its own: `project-setup`, `pm-tailoring` and `pm-coach`. The skills that keep
a register are named in [Registers and their keepers](registers-and-keepers.md).

## Set up and adapt

| Skill | Ask it to |
|---|---|
| `project-setup` | set up or review the project's configuration (`PROJECT.md` and `TOOLS.md`), over one or more sessions |
| `pm-tailoring` | adapt the plugin to the way your project works, with the lightest change that does it |
| `pm-coach` | advise you on what to do next and how, grounded in your registers; it never writes |

## Start the project and define its scope

| Skill | Ask it to |
|---|---|
| `project-charter` | draft or revise the project charter from the registers, and propose initial risks, stakeholders and gates |
| `wbs-builder` | build the work breakdown structure and its dictionary, checked against the 100% rule |
| `product-roadmap` | draft or revise the product roadmap: Product Goal, themes and horizons |
| `backlog-refinement` | review the top of the backlog for readiness, splits and order |
| `release-plan` | plan a release: scope by likelihood, 50/85/95% dates, criteria and dependencies |

## Plan and run sprints

| Skill | Ask it to |
|---|---|
| `sprint-planning` | draft the sprint plan against capacity and recent throughput |
| `sprint-review` | draft the sprint review: what was delivered against the Sprint Goal, and the feedback |
| `retrospective` | prepare and record a retrospective, with owned and dated actions |

## Schedule, estimates and forecasts

| Skill | Ask it to |
|---|---|
| `estimate` | produce three-point or analogous estimates of effort and cost |
| `schedule-check` | check the critical path, float and slip against the baseline |
| `flow-metrics` | compute cycle time, throughput, WIP and work item age at team level |
| `delivery-forecast` | forecast when N items will be done, or how many by a date, as ranges |

## Money

| Skill | Ask it to |
|---|---|
| `budget-tracker` | keep the budget and track spend with earned value |

## Risk, change and decisions

| Skill | Ask it to |
|---|---|
| `risk-register` | identify, assess, respond to and review risks |
| `change-request` | raise a change request, assess its impact and record who decided |
| `decision-log` | record a decision, or answer what was decided and why |
| `phase-gate-review` | prepare a gate review and record its outcome once those with authority decide |

## People and responsibilities

| Skill | Ask it to |
|---|---|
| `team-register` | keep the team register and reconcile it with recent activity |
| `capacity-register` | keep calendar, allocation and absences, and compute available person-days |
| `raci-matrix` | keep the RACI matrix, with one accountable role per deliverable |
| `assignment-advisor` | suggest up to three people to take a task or a review, with reasons |
| `team-charter` | prepare the team charter workshop and record the team's agreements |

## Stakeholders and communication

| Skill | Ask it to |
|---|---|
| `stakeholder-register` | keep the stakeholder register, with interest, influence, engagement and approach |
| `communication-plan` | draft the communication plan: who receives what, when and how |
| `status-report` | draft the status report for the reporting period, outcomes first |
| `actionable-message` | write an email or chat message where every request has an owner, a deadline and references, in a strong or friendly format, ready to paste into an email client or a chat (see [Messages](messages.md)) |
| `publish-deliverable` | render a Markdown document into Word, PDF, slides, email or an artifact, and send it on request |

## Meetings, actions and incoming material

See [Meetings](meetings.md), [Actions and the PM backlog](actions-and-backlog.md) and [The inbox](inbox.md).

| Skill | Ask it to |
|---|---|
| `meeting-prep` | prepare a meeting and write its brief |
| `meeting-minutes` | write the minutes from notes, a transcript or a tool, or import minutes written by others |
| `action-log` | add or close an action, or show your PM backlog |
| `inbox-triage` | classify what is in the inbox and route each file |

## Learn

| Skill | Ask it to |
|---|---|
| `lessons-learned` | write what a project or phase learned, backed by facts and never about people |

## Agents

Agents do read-only work in a context of their own, for the skills that use them.

| Agent | What it does |
|---|---|
| `project-activity-scout` | collects recent activity from the project's tools |
| `flow-data-scout` | collects the transition history of work items, without assignees |
| `pm-critical-reviewer` | challenges plans, estimates, risk responses, impact analyses and deliverables before they go out |
| `register-reviewer` | checks the registers for consistency with each other and, with collected facts, with the real state of the project |
