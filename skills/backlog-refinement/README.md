---
summary: For product owners and project managers - checks the readiness of the top of the backlog, proposes splits and an order with reasons, flags stale and duplicate items, and writes back to the issues tool only on confirmation.
---

# backlog-refinement

Reviews the top of the product backlog in the project's issues tool. It checks whether each item is ready to be
planned, proposes how to split the big ones, proposes an order with the reason for each place, and flags items that
have gone stale or appear twice.

## Why

Refinement drifts: items reach sprint planning without acceptance criteria, epics sit at the top for months, the same
request is filed twice. This skill reads the backlog, the project's Definition of Ready when it has one, the roadmap
and the registers, and gives the Product Owner a short, reasoned list of what to fix before planning. It proposes;
the order stays the Product Owner's decision, and nothing changes in the issues tool without your confirmation.

## Use cases

### Get the backlog ready for sprint planning

**Context:** Sprint planning is on Monday and the top of the backlog was last refined a month ago.

**Action:** Ask "is the backlog ready for the next two sprints?".

**Result:** A table of the top items marked ready, nearly or not ready, with what each is missing, and draft
acceptance criteria to confirm for the ones that lack them.

### Split an epic that does not fit in a sprint

**Context:** An epic about user onboarding sits at the top of the backlog with no size.

**Action:** Ask "split ACME-412".

**Result:** Proposed parts, each with an outcome and acceptance criteria, and the splitting approach chosen with its
reason; once you confirm the itemized list, the parts are created through the issues tool when it allows writes.

### Clean up stale and duplicate items

**Context:** The backlog has grown past two hundred items.

**Action:** Ask "raffiniamo il backlog: cosa è vecchio o duplicato?".

**Result:** Items untouched for long, made obsolete by a decision or a release, or overlapping another, each with a
proposal to keep, merge or close and its reason; nothing is closed on its own.

## Usage

Ask in your own words ("refine the backlog", "propose an order for the top items", "backlog pronto?") or run
`/pm-skills:backlog-refinement`.

## Inputs and outputs

- Reads `PROJECT.md` (declared in `AGENTS.md` or `CLAUDE.md`), the `backlog-refinement` section of `TAILORING.md`
  (for example the Definition of Ready), the decision log, the risk register, the change log and the product roadmap,
  and the backlog through the issues capability in `TOOLS.md`.
- Outputs the readiness table, splits, the proposed order, stale and duplicate items, and the sources read.
- Writes to the issues tool only through a tool declared with Mode `write`, each change or an itemized batch
  confirmed by you.

## Requirements

A project register (`/pm-skills:project-setup`) and an issues tool in `TOOLS.md`. Without the tool, the skill works on
items you paste.

## Limitations

- It does not estimate on the team's behalf; an estimate you ask for is a proposal for the team.
- Without a Definition of Ready in the tailoring register, readiness is checked against general criteria.
- It reviews the top of the backlog, not the whole backlog at once.
