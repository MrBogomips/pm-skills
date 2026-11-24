---
summary: For project managers - drafts the status report for the reporting period from the project's registers and tools, outcomes first, with colors backed by facts and a critical review for steering committees and clients.
---

# status-report

Drafts the status report for the current reporting period: summary, outcomes, schedule, scope, budget, risks and
issues, decisions, next period and sources. The facts come from the project's tools, through the
`project-activity-scout` agent, and from the risk register, the decision log and the previous report.

## Why

A status report written from memory lists activities, hides slippage behind a green light and cannot be compared with
the last one. This skill sets the period from the reporting cadence and the previous report, gathers the facts
before drafting, puts outcomes before activities, gives every color its reason and names every source it could not
read. A report for a steering committee or the client is challenged by a critical reviewer before you see it.

## Use cases

### The biweekly report for the team

**Context:** Acme Portal reports every two weeks; the last report closed on 2026-11-10.

**Action:** Ask for "the status report".

**Result:** A draft for 2026-11-11..2026-11-24, with issues closed, pull requests merged and releases of the period,
the risks that changed and the decisions taken, written as a draft after your agreement.

### The SAL for the client

**Context:** The report goes to the client's steering committee, and the project calls it "SAL".

**Action:** Ask "prepara il SAL per il comitato".

**Result:** The draft titled as the project wants, with the client's extra section; before you see it, a critical
review (announced, with a stronger model you can decline) whose open points come with the draft.

## Usage

Ask in your own words ("status report", "SAL", "report di avanzamento") or run `/pm-skills:status-report`. Say the
period or the audience if you know them; otherwise the skill proposes them and asks.

## Inputs and outputs

- Reads `PROJECT.md` (cadence, naming, language, registers), `TAILORING.md`, `RISKS.md`, `DECISIONS.md`, `TEAMS.md`
  and the previous report, and the project's tools through `TOOLS.md`.
- Writes one report in the folder of the project's Working documents section, named by
  `shared/scripts/doc_naming.py`, in the format of
  [`shared/documents/status-report.md`](../../shared/documents/status-report.md): first as `draft`, then `issued`
  when you approve it.

## Requirements

A project register (`/pm-skills:project-setup`) and, for facts from the tools, a tools register. The
`project-activity-scout` and `pm-critical-reviewer` agents ship with the plugin.

## Limitations

- Reports only what the registers and tools show; a missing source leaves a stated gap, never an estimate.
- Budget is "not tracked here" without a `costs` tool.
- Never sends the report: use `/pm-skills:publish-deliverable`.
