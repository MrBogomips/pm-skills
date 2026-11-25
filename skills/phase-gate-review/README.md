---
summary: For project managers and sponsors - keeps GATES.md and prepares gate reviews that assess each criterion against evidence, recording the outcome only once the deciders have decided.
---

# phase-gate-review

Keeps the project's gate register and prepares the review of a phase gate or of the project's close. Each criterion
is assessed against evidence from the registers and the tools, the conditions of earlier outcomes are followed up,
and the draft is challenged before the people who decide read it. The outcome is recorded only once they have decided.

## Why

Gate reviews often turn into a slide that says "green" with no evidence behind it, and the conditions attached to a
"go" are forgotten once the meeting ends. This skill keeps the criteria, every outcome and its conditions in one
register, assesses each criterion with its source or marks it `no evidence`, and brings the open conditions back at
the next review. It never decides the gate: it records the decision the steering committee or the sponsor took.

## Use cases

### Prepare a go-live review

**Context:** Acme Portal's gate G-002 "Go-live readiness" is planned for Friday; the security sign-off is still
missing.

**Action:** Ask "prepare the gate review for G-002".

**Result:** A draft with each criterion `met`, `partly met`, `not met` or `no evidence` and its source, open risks
that bear on the decision, a recommendation, and the critical reviewer's findings; challenged in depth because the steering committee decides.

### Record the decision

**Context:** The steering committee decided "go with conditions": pen test fixes by 11 December.

**Action:** Ask "record the outcome of gate G-002" and say who decided and on what date (Italian works too).

**Result:** The outcome appended to `GATES.md`, the gate marked `passed`, the Decision filled in the review; at the
next review of the gate the condition comes back with its state.

## Usage

Ask in your own words ("phase gate", "go/no-go", "revisione di fase") or run `/pm-skills:phase-gate-review`. Say
whether you are defining gates, reviewing one or recording a decision; the skill asks if it cannot tell.

## Inputs and outputs

- Reads `PROJECT.md`, `TAILORING.md`, `GATES.md`, the risk, change, decision, schedule and budget registers, the
  RACI matrix, the charter, the release plan, earlier reviews, and the `ci`, `releases`, `issues` and `incidents`
  tools through `TOOLS.md`.
- Writes `GATES.md` in the format of [`shared/registers/gates.md`](../../shared/registers/gates.md), validated by
  `shared/scripts/gates_register.py`, and gate reviews in the format of
  [`shared/documents/phase-gate-review.md`](../../shared/documents/phase-gate-review.md).
- Review documents go in the folder of the project's Working documents section, as drafts until issued.

## Requirements

A project register (`/pm-skills:project-setup`) is recommended. A tools register for the evidence from the tools.

## Limitations

- Never records an outcome you did not report, and never turns its recommendation into a decision.
- The criteria of a gate with an outcome are frozen; a changed gate becomes a new gate.
- Does not check that a `Milestone` exists in the schedule register.
