---
summary: For project managers and Product Owners - drafts the release plan with its goal, a scope cut into likely, at risk and unlikely by a throughput forecast, 50/85/95% dates, release criteria from the Definition of Done, dependencies and approved changes.
---

# release-plan

Drafts the plan of a release: what it is for, which items are likely to make it by the date, when it is likely to
ship, what it has to meet before it goes out, and what it depends on. Dates and the scope cut come from a Monte Carlo
forecast of the team's throughput; commitments come only from the contract, the decision log or approved change
requests.

## Why

A release plan built on wishes becomes a list of broken promises. This skill forecasts the release from the team's
own throughput, cuts the ordered scope at the 85% and 50% lines so everyone sees which items are safe and which are
not, keeps committed dates apart from forecast ones, and shows plainly when the commitment and the forecast disagree,
with the options to resolve it. Each revision reruns the forecast and records what moved.

## Use cases

### Plan a release with a committed date

**Context:** Acme Portal 2.0 is due on 15 January by an approved change request; its fix version holds 30 items.

**Action:** Ask "plan release 2.0".

**Result:** A draft with the 30 items cut into likely, at risk and unlikely at 15 January, the forecast dates for the
whole scope, the release criteria from the Definition of Done and CR-004 under Approved changes; if the committed
scope falls beyond the 85% line, Dates says so and lists the options.

### Revise the plan two weeks later

**Context:** The plan exists at version 1.0.0; three items were added and five finished.

**Action:** Ask "aggiorna il piano di rilascio".

**Result:** A new snapshot and forecast, items moved between bands, Changes from the previous version filled, and the
version raised.

## Usage

Ask in your own words ("release plan", "piano di rilascio") or run `/pm-skills:release-plan`. Name the release; the
skill finds its items in the issues or releases tool, or asks.

## Inputs and outputs

- Reads `PROJECT.md` (Definition of Done, Definition of Workflow, naming, language, registers), `TAILORING.md`,
  `CHANGES.md`, `DECISIONS.md`, `RISKS.md`, `CAPACITY.md`, the latest roadmap and the previous plan, and the issues
  and releases tools through `TOOLS.md`, via the `flow-data-scout` agent for the history.
- Writes a snapshot, after you agree, in the flow data folder (default `flow/`), and one plan in the documents folder
  of the project's Working documents section, named by `shared/scripts/doc_naming.py`, in the format of
  [`shared/documents/release-plan.md`](../../shared/documents/release-plan.md).
- Changes nothing in the tools.

## Requirements

A project register (`/pm-skills:project-setup`), a tools register with an `issues` tool that keeps the transition
history, and a Definition of Done for the release criteria; without it the plan lists release-level criteria only.

## Limitations

- The forecast counts items and assumes the scope does not grow; revise the plan when it does.
- It never cuts scope or moves the date itself: it shows the options and you decide.
- It does not change fix versions or the order of the backlog.
