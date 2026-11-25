---
name: estimate
description: Estimates effort and cost - three-point (PERT) ranges per item and in total, analogous estimates from past work, cost from the rates per role in BUDGET.md - with every number from a script and the assumptions stated. Use for "estimate this", "how much effort", "how much will it cost to build", "three-point estimate"; not spend to date (budget-tracker).
---

# Estimate

Turns ranges and past work into effort and cost estimates the user can defend: each number computed by a script,
each assumption written down. The estimate is shown, not stored, unless the user asks to write it somewhere.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **Project register**: `PROJECT.md`, declared in the project's `AGENTS.md` (or `CLAUDE.md`) as
  `- Project register: \`<path>\``: `Contract type`, `Deliverable language`, the Registers. With no project
  register, suggest `/pm-skills:project-setup`; the user may still estimate in the session, giving what you would
  have read there.
- **Registers, read only**: budget register (rates per role, format `${CLAUDE_PLUGIN_ROOT}/shared/registers/budget.md`),
  team register (roles), capacity register, risk register, change log; the `## estimate` section of the tailoring
  register.
- **Tool capabilities** (through `TOOLS.md`): `issues` for the items to estimate and for past items comparable in
  kind and size (their estimates and actual effort or elapsed time); `costs` when rates live there instead of
  `BUDGET.md`.
- **Agent**: `pm-critical-reviewer` (challenge of high-stakes estimates).
- **From the user**: what to estimate, and for each item an optimistic, most likely and pessimistic effort, or a
  single figure with how sure they are; the role that does the work; the purpose (internal plan, quote to the client,
  change request).

## Steps

1. **Start.** Read the project register, the budget register and the tailoring section; say which rules apply.
2. **Frame.** Restate the scope being estimated, the unit (hours or days), the purpose and the audience. Break large
   items into parts the user can range; leave out nothing the user named, and list what is out of scope.
3. **Pick the technique** and say why:
   - **three-point** when the user gives ranges, or can: ask for them; never turn a single figure into a range
     yourself;
   - **analogous** when comparable past items exist in `issues`: show which items, their size and actual effort,
     and how the new work differs (scale, technology, team, dependencies). The model proposes the analogy; the user
     accepts or adjusts the ranges it suggests.
   Consider for software work: integration and testing, reviews, technical debt touched, dependencies, release and
   environment work, and the Definition of Done.
4. **Compute effort.** One item:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/estimate.py" pert --optimistic <O> --likely <M> --pessimistic <P> --unit <days|hours>`.
   Several items: write a temporary CSV `item,optimistic,likely,pessimistic` in the session scratchpad (never in the
   project) and run `... estimate.py pert --items <file> --unit <days|hours>`. Show the script's output: mean, standard
   deviation, ranges and the 50/85/95% values, saying they use a normal approximation that assumes independent items.
5. **Compute cost**, per role, from the rate in force on the date of the work:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/estimate.py" cost --budget <BUDGET.md> --role <role> --effort <N> --unit day|hour --date <D> [--hours-per-day <H>]`.
   Run it for the effort at each confidence level the user wants. When the effort unit differs from the rate's unit
   the script needs `--hours-per-day`: ask the user for it, never assume one. Check the role against the team register's roles
   and the Rates table; a missing rate is asked for, never assumed. With rates only in a `costs` tool, read them
   there and say so; with no rates at all, give effort only. Add non-labor costs only as the user gives them.
6. **Challenge** with `pm-critical-reviewer` before presenting when the stakes are high: a quote to the client, a
   change request, a fixed-price contract, or a total the tailoring `rules` name as a threshold. Give it the facts
   only: the draft estimate, purpose and audience, register paths, the past items used and the script outputs with
   their date. Fold its findings in or show them as open points.
   **Fable escalation**: for a quote to the client or an estimate for a steering committee, dispatch the reviewer
   with the model set to `fable`; tell the user before dispatching, and why.
7. **Present**, in the user's language (the `Deliverable language` for a text that goes out): scope and out of
   scope; per item O/M/P, mean and standard deviation; totals at 50/85/95%; cost per role and in total at the
   levels chosen; the assumptions, the risks that would move the estimate (suggest `/pm-skills:risk-register` for
   new ones) and the sources read or not read. Recommend which confidence level fits the purpose, and why.
8. **Write elsewhere only on request.**
   - Estimates on issues: only through an `issues` tool with `Mode: write`; show the itemized list (item, field,
     value) and write only what the user confirms. Report each write and any that failed.
   - For a change request, suggest `/pm-skills:change-request` and hand it the figures to cite.

## Always

- Every number from the scripts, never from your own arithmetic; show the commands' output.
- Effort by role and by team; cost from rates per role.
- Name the confidence level of every figure; never a single number without its range.
- Keep the user's ranges apart from the ones you proposed by analogy, and say which past items you used.

## Never

- Never estimate or record the cost of a named person, or ask for anyone's salary or personal rate.
- Never invent a range, a rate or a past actual; a gap is a question.
- Never write `BUDGET.md`, the change log or any register from here; suggest `/pm-skills:budget-tracker` or
  `/pm-skills:change-request`.
- Never write to the issues tool without a `Mode: write` tool and the user's confirmation on the itemized list.

## Extension points

- `scale`: the default confidence level for quotes and for internal plans, the unit, the threshold that makes an
  estimate high-stakes.
- `rules`: required review or approval before an estimate goes to the client, contingency to state.
- `steps`: extra steps before computing or before presenting.
- `terms`: the project's words for effort, confidence levels and roles.
