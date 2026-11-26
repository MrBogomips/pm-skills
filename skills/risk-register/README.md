---
summary: For project managers - keeps RISKS.md, the register of threats and opportunities with their assessment, response, owner and review date, and reviews it against the project's facts.
---

# risk-register

Keeps `RISKS.md`, the project's risk register. It sets the register up, turns what you say or what the project's
tools show into risk statements, assesses them on the project's scale, plans responses with owners and review
dates, and reviews the register when risks come due.

## Why

A risk list written at kick-off and never opened again protects no one. This skill keeps the register alive: it
reads the decision log, open issues, incidents, CI and releases to find risks you have not written down, proposes
assessments and responses with their reasons, brings up risks past their review date, and has the critical
reviewer challenge the responses to high risks. It writes only what you accept, and the validator checks every
score.

## Use cases

### Find the risks nobody wrote down

**Context:** The project has a register with a few risks from the kick-off and a release coming in December.

**Action:** Ask "look for new risks in the project".

**Result:** A numbered list of candidate risks, each tied to the fact it comes from (a blocked issue, a recent
incident, a new dependency in the decision log), with a proposed assessment; the ones you accept are added with the
next IDs.

### Review the risks that came due

**Context:** The session starts with "1 past their review date".

**Action:** Ask "review the risks".

**Result:** Overdue risks first, then high ones, each with a proposed re-assessment, new response or closure; once
the whole register is reviewed, `Last reviewed` moves to today.

### Challenge the response to a high risk before the steering committee

**Context:** A high risk needs a response you will present to the steering committee.

**Action:** Ask "review the response to R-001 for the steering committee".

**Result:** The critical reviewer challenges the response on the facts; the skill says beforehand that it uses a
stronger model for this review, and proposes changes you accept or reject.

## Usage

Ask in your own words ("add a risk: the payment provider may slip", "review the risks") or run
`/pm-skills:risk-register`. Without a risk register the skill starts by setting one up.

## Inputs and outputs

- Reads `PROJECT.md` (declared in `AGENTS.md` or `CLAUDE.md`), the `risk-register` section of `TAILORING.md`, the
  decision log and the team register, and the project's tools by capability (issues, incidents, code, CI,
  releases) as listed in `TOOLS.md`.
- Writes `RISKS.md` in the format of [`shared/registers/risks.md`](../../shared/registers/risks.md), and once, with
  your consent, the `Risk register` line in `PROJECT.md`.
- Sends an escalation message only through a messaging tool declared with Mode `write`, after you agree.
- Takes changes handed off by other skills (for example from meeting minutes), checks them against its own rules, and reports the IDs it assigned.

## Requirements

A project register (`/pm-skills:project-setup`). The tools register is optional: without it the skill works from
what you tell it and says which sources it could not read.

## Limitations

- Scores are Probability × Impact on a single scale; other scoring models are not supported.
- What counts as high, and where high risks go, comes from the project's tailoring or the default (60% of the
  highest score).
- No personal data and no judgment of people: a risk about people is stated as a delivery fact.
