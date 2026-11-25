---
summary: For project managers, Scrum Masters and Kanban teams - computes the team's cycle time, throughput, WIP and work item age against the SLE from a saved snapshot of the transition history, compares snapshots over time, and adds the DORA metrics when the tools allow.
---

# flow-metrics

Computes the team's flow metrics from the transition history of its work items: cycle time percentiles, throughput
per week, work in progress, and the age of items in progress against the Service Level Expectation of the Definition
of Workflow. The history is saved in the project as a snapshot, so the metrics can be recomputed and compared later.

## Why

Flow metrics read off a board's charts are hard to check and impossible to compare months later, when the board has
changed. This skill collects the transition history once, saves it as a plain CSV with no people in it, and has a
tested script compute every number, so the team sees the same figures each time and can compare this quarter with
the last. It flags the items aging past the SLE while there is still time to act, and adds deployment frequency,
lead time, change failure rate and time to restore when the release and incident tools are declared.

## Use cases

### Find the items that are aging

**Context:** Acme Portal's Definition of Workflow sets the SLE at 85% of items in 10 days.

**Action:** Ask "which items are aging?".

**Result:** A fresh snapshot, saved after you agree, and the items in progress past or close to 10 days, by key,
with WIP against the limits and questions for the team about where the items wait.

### Compare with last quarter

**Context:** The project folder holds a snapshot from August.

**Action:** Ask "confronta le metriche di flusso con agosto".

**Result:** The two snapshots side by side with the same workflow mapping: cycle time percentiles, throughput and WIP,
and what moved.

### DORA metrics

**Context:** `TOOLS.md` declares GitHub for `code`, `ci` and `releases` and an incident tracker for `incidents`.

**Action:** Ask "DORA metrics for the last three months".

**Result:** Deployment frequency, lead time for changes, change failure rate and time to restore, computed by a
script from temporary files that are not kept; any metric whose data is missing is named and left out.

## Usage

Ask in your own words ("flow metrics", "cycle time", "metriche di flusso", "tempo di ciclo") or run
`/pm-skills:flow-metrics`. Say the period or the snapshot to compare with if you have one in mind.

## Inputs and outputs

- Reads `PROJECT.md` (Definition of Workflow, language, registers), `TAILORING.md`, the Definition of Workflow file,
  and the issues tool through `TOOLS.md` via the `flow-data-scout` agent; for DORA, the `releases`, `code`, `ci` and
  `incidents` tools.
- Writes one snapshot per collection, after you agree, in the flow data folder of the project's Working documents
  section (default `flow/`), in the format of
  [`shared/registers/flow-snapshot.md`](../../shared/registers/flow-snapshot.md): items and transitions only.
- Answers in the conversation; it writes no document and changes nothing in the tools.

## Requirements

A project register (`/pm-skills:project-setup`) and a tools register with an `issues` tool that keeps the transition
history. A Definition of Workflow with the started and finished points and the SLE; without it the skill falls back
to the board's configuration or asks.

## Limitations

- Team-level only: the snapshot has no person column and the skill never compares people.
- The metrics are as good as the history: statuses renamed or skipped in the tool show up as gaps.
- DORA metrics need deployment and incident data in a declared tool; lead time needs commit times.
