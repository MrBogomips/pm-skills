---
summary: For project managers and Product Owners - forecasts when a number of items will be done, or how many by a date, with a Monte Carlo simulation of the team's weekly throughput, always as 50/85/95% ranges with their assumptions.
---

# delivery-forecast

Forecasts delivery from the team's own history: "when will these 40 items be done?" or "how many items can we finish
by 15 January?". A script runs a Monte Carlo simulation over the weekly throughput of a saved snapshot and gives the
answer at 50%, 85% and 95%, with the assumptions it rests on.

## Why

A single date from an estimate hides how uncertain it is, and the team pays for it later. Throughput history already
holds that uncertainty: the weeks when much finished and the weeks when nothing did. This skill samples it thousands
of times with a tested script, so the answer comes as a range you can commit against, the 85% line, with the
assumptions spelled out (history window, stable process, scope not growing) and the snapshot saved for the next
check.

## Use cases

### When will the epic be done

**Context:** The Acme Portal checkout epic has 24 items not done.

**Action:** Ask "when will the checkout epic be done?".

**Result:** The 24 items counted from the issues tool, the dates at 50%, 85% and 95%, the 85% line recommended for a
commitment, and the assumptions with the number of weeks of history used.

### How many by a date

**Context:** The client asks what can be in the release of 15 January.

**Action:** Ask "how many items can we close by 15 January?".

**Result:** At least N items in 85% of runs, M in 50%, with the holidays in the window from the capacity register and
a suggestion to turn it into a release plan.

## Usage

Ask in your own words ("when will it be done", "forecast", "how many items by") or run `/pm-skills:delivery-forecast`.
Name the scope (a release, an epic, a filter) or the number of items, and the date for a how-many forecast.

## Inputs and outputs

- Reads `PROJECT.md` (Definition of Workflow, language, registers), `TAILORING.md`, `CAPACITY.md`, the Definition of
  Workflow file, and the issues tool through `TOOLS.md`, via the `flow-data-scout` agent for the history.
- Writes a snapshot, after you agree, in the flow data folder of the project's Working documents section (default
  `flow/`), in the format of [`shared/registers/flow-snapshot.md`](../../shared/registers/flow-snapshot.md).
- Answers in the conversation; it writes no document and changes nothing in the tools.

## Requirements

A project register (`/pm-skills:project-setup`) and a tools register with an `issues` tool that keeps the transition
history; enough history to sample, ideally ten weeks or more.

## Limitations

- It counts items, not points or hours: it assumes the mix of item sizes stays as it was.
- It does not model scope growth: rerun it when items are split or added.
- A change of team or workflow makes the history a poor guide; the skill says so but cannot correct for it.
