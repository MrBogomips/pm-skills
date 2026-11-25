---
summary: For project managers - keeps CHANGES.md, the change log, with each change request's impact on scope, schedule, cost and risk, a critical review of the analysis, who decided and when, and its implementation.
---

# change-request

Keeps `CHANGES.md`, the project's change log. It raises a change request, assesses its impact on scope, schedule,
cost and risk from the project's registers and tools, has the analysis challenged before you rely on it, records the
decision and who took it, and marks the change implemented.

## Why

A change agreed in a corridor turns up later as a missed date or an invoice nobody expected. This skill puts every
change through the same path: what is asked and why, what it does to scope, schedule, cost and risk with the facts
behind each impact, a critical review of that analysis, a decision by the approvers your project names, and a link
to the decision log. It never invents an approver, an estimate or a rate, and the validator keeps the history
intact.

## Use cases

### Assess a change the client asked for

**Context:** In the steering committee the client asks to add single sign-on for partners before the December
release.

**Action:** Ask "raise a change request: SSO for partners before the December release, asked by the client".

**Result:** CR-004 is raised as proposed; the skill reads the backlog, the capacity register, the schedule and the
rates per role, drafts the four impacts with their sources, has the critical reviewer challenge them (with a
stronger model, announced beforehand, because three impacts are not `none`), and names the approvers the project's
tailoring requires above its threshold.

### Record the decision

**Context:** The steering committee approved CR-004 on 2026-11-27.

**Action:** Ask "CR-004 approved by the steering committee on 27 November".

**Result:** CR-004 moves to approved with who decided and when; the skill offers a D-NNN entry for the decision log
and proposes the new risk the change creates for the risk register, writing each only if you agree.

### Close the loop

**Context:** The SSO work was released.

**Action:** Ask "segna la CR-004 come implementata".

**Result:** CR-004 moves to implemented with the release date, checked against the release the tools show.

## Usage

Ask in your own words ("change request", "valuta l'impatto della modifica") or run `/pm-skills:change-request`.
Without a change log the skill starts by setting one up.

## Inputs and outputs

- Reads `PROJECT.md` (declared in `AGENTS.md` or `CLAUDE.md`), the `change-request` section of `TAILORING.md`,
  the risk register, decision log, team register and capacity register, and the project's tools by capability
  (issues, schedule, costs, releases) as listed in `TOOLS.md`.
- Writes `CHANGES.md` in the format of [`shared/registers/changes.md`](../../shared/registers/changes.md), and once,
  with your consent, the `Change log` line in `PROJECT.md`.
- With your agreement, appends a decision to the decision log and new risks to the risk register.
- Dispatches the `pm-critical-reviewer` agent on every impact analysis.

## Requirements

A project register (`/pm-skills:project-setup`). The tools register is optional: without it the impacts rest on
what you tell the skill and on the registers, and it says which sources it could not read. Approval thresholds and
approvers come from `rules` in `TAILORING.md`; without them the skill asks who decides.

## Limitations

- Effort and cost come from your estimates and the rates the costs tool holds; the skill does not estimate.
- Existing decisions and risks are not edited here: superseding a decision or re-assessing a risk goes to
  `/pm-skills:decision-log` and `/pm-skills:risk-register`.
- A decided request is not rewritten: a change of mind is a new request.
