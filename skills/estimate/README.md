---
summary: For project managers - three-point (PERT) and analogous estimates of effort and cost, every number from a script, cost from the rates per role in BUDGET.md, and high-stakes estimates challenged before they go out.
---

# estimate

Turns the team's ranges and the project's past work into effort and cost estimates: PERT means and confidence
levels per item and in total, analogies with comparable past items, and cost from the rates per role in the budget
register. The estimate is shown, with its assumptions, and written into the issues tool or a change request only if
you ask.

## Why

A single number said in a meeting becomes a commitment. This skill keeps the range attached to every figure, says
which confidence level a total stands for, and computes everything with a script so nobody has to trust mental
arithmetic. When the estimate goes to the client or into a change request, the critical reviewer challenges it first
for optimism, missing work and unstated assumptions.

## Use cases

### Three-point estimate of a feature

**Context:** The team gives ranges for the five stories of the payment feature.

**Action:** Ask "stima a tre punti di queste cinque storie" with the ranges.

**Result:** Per story the PERT mean and standard deviation, the total at 50, 85 and 95%, the note that the totals use
a normal approximation, and the assumptions behind them.

### Quote for a change requested by the client

**Context:** Acme Corp asks for an export feature; `BUDGET.md` has the rates per role.

**Action:** Ask "how much will the export feature cost? It's for a quote to the client".

**Result:** Effort ranges, cost per role at the confidence level recommended for a quote, the reviewer's findings
folded in or listed as open points, and the suggestion to raise it with `/pm-skills:change-request`.

### Analogous estimate from past work

**Context:** The issues tool holds a similar integration finished three months ago.

**Action:** Ask "estimate the new integration based on the last one".

**Result:** The past item, its actual effort and how the new work differs, with proposed ranges you accept or adjust
before the script computes the totals.

## Usage

Ask in your own words ("how much effort is this", "quanto costa") or run `/pm-skills:estimate`.

## Inputs and outputs

- Reads `PROJECT.md` (declared in `AGENTS.md` or `CLAUDE.md`), the `estimate` section of `TAILORING.md`, the
  budget register (rates per role), the team register (roles), and the issues and costs tools listed in `TOOLS.md`.
- Writes nothing in the project. Temporary inputs for the script stay in the session's scratch space.
- Writes estimates to the issues tool only through a tool declared with Mode `write`, after you confirm the itemized
  list.

## Requirements

Python 3 for the shared scripts. A project register (`/pm-skills:project-setup`) and, for cost, a budget register
(`/pm-skills:budget-tracker`); without rates the skill gives effort only.

## Limitations

- Totals at 50, 85 and 95% use a normal approximation that assumes independent items.
- Cost is labor by role; other costs only as you give them. No individual cost, ever.
- The skill does not store estimates; record them in a change request or the issues tool.
