---
name: status-report
description: Drafts the project status report for the reporting period from the registers and the project tools, outcomes before activities, with status colors backed by facts and a critical review when it goes to a steering committee or the client. Use for a status, progress, weekly or monthly report ("status report", "progress report", "weekly report", "highlight report").
---

# Status report

Writes the status report for one reporting period: where the project stands, what it delivered, what is at risk and
what the reader has to decide, every claim backed by a register or a tool.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **The project register**: `PROJECT.md`, declared by `` - Project register: `PROJECT.md` `` in the project's
  `AGENTS.md` (or `CLAUDE.md`): `Project name`, `Internal code`, `Client`, `Contract type`, `Deliverable language`,
  the Profile key `Reporting cadence`, the naming Conventions and the Registers. With no project register, suggest
  `/pm-skills:project-setup`; you may still draft in the session if the user wants, asking for what you would have
  read there and inventing no configuration.
- **Registers**, when declared: risk register, decision log, team register, tools register, tailoring register.
- **Tool capabilities** (through `TOOLS.md`): `issues`, `code`, `ci`, `releases`, `incidents` (via the agent),
  `schedule` for milestones, `costs` for the budget.
- **Formats**: `${CLAUDE_PLUGIN_ROOT}/shared/documents/status-report.md` and
  `${CLAUDE_PLUGIN_ROOT}/shared/documents/common.md`.
- **Agents**: `project-activity-scout` (facts), `pm-critical-reviewer` (review).

## Steps

1. **Read the configuration** and the `## status-report` section of `TAILORING.md`; say which rules you will apply.
2. **Set the period.** Find the previous report in the documents folder (from the Working documents section) by the
   naming convention: the latest `status-report/<date>-status-report*.md`, or the highest `<PROJ>-<CODE>-NNN` with
   the type code from Conventions (default `SR`). The period starts the day after the previous `period` ends and
   spans one `Reporting cadence`, ending on its last day or today. With no cadence, no previous report or a cadence
   in free text you cannot apply, propose a period and ask.
3. **Ask who reads it** when you cannot tell: the team, a sponsor, a steering committee, the client. It decides the
   tone and step 6.
4. **Gather the facts.**
   - Dispatch `project-activity-scout` in per-project mode with the path of `PROJECT.md` and the window in days from
     the start of the period to today; wait for its report, including its "Sources checked".
   - Read the risk register (changes in the period, top open risks, occurred ones), the decision log (decisions dated
     in the period), the team register (joins and departures, as facts), the previous report (to compare), and the
     `schedule` and `costs` tools when declared.
5. **Draft** in the format, in the `Deliverable language`. Outcomes first, as value delivered, then the evidence.
   Every color has its reason, by the format's rule or the `scale` rules; every number comes from a register, a tool
   or a plugin script. Keep facts apart from inferences, and put in Sources what was read, with the date of the data,
   and what could not be read. Compare with the previous report where it helps: what moved, what slipped.
6. **Review**, when the report goes to a steering committee or the client: tell the user that the draft goes to
   `pm-critical-reviewer` with the model escalated to `fable`, because it is a deliverable for a steering committee
   or a client; the user may decline the escalation, and the review then runs on the agent's own model. Give the
   reviewer the draft and the facts from step 4; it gathers nothing. Address its findings or show them to the user.
7. **Name and show.** Name the file with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/doc_naming.py" next --project <PROJECT.md> --dir <folder> --type status-report --date <end of period>`
   (exit status 3: the report for that date exists; revise it instead). Show the draft, the path and the review's
   open points. Write it with `status: draft`, `version: 1.0.0`, only after the user agrees.
8. **Issue.** When the user approves, set `status: issued`. A later change to an issued report raises the version
   (`doc_naming.py bump <version> major|minor|patch`). Suggest `/pm-skills:publish-deliverable` to share it.

## Always

- A heading with nothing to report keeps a one-line "nothing to report", so reports compare.
- Delivery facts by team or by person only; no names of people in judgments, no sensitive personal data.
- Name every source that could not be read and what the report cannot say because of it.
- Show before writing; write only after the user agrees.

## Never

- Never fill a gap with an estimate made while writing, and never write a color without its reason.
- Never send, upload or publish the report: that is `/pm-skills:publish-deliverable`'s job, on the user's request.
- Never write to the registers from here: suggest `/pm-skills:risk-register` or `/pm-skills:decision-log` for what
  they miss.

## Extension points

- `format`: sections added to or renamed in the report, or a project template.
- `scale`: the thresholds of the status colors, overall and per heading.
- `rules`: extra checks or approvals, such as a sponsor's approval before issuing.
- `steps`: extra steps before drafting, before the review, or after issuing.
- `terms`: the project's words for the report and its parts ("highlight report").
