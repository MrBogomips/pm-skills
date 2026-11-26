---
summary: For project managers and sponsors - drafts the project charter from the registers, has it challenged, and seeds the risk, stakeholder and gate registers on your confirmation.
---

# project-charter

Drafts the project charter: purpose, objectives and success criteria, scope in and out, milestones, phases and gates,
constraints, budget, risks, stakeholders and authority. It reads what the registers already hold, asks only for what
they do not, has the draft challenged before it goes out, and proposes the initial entries of the registers that are
still empty.

## Why

A charter written once in a word processor drifts away from the registers within weeks, and nobody can say which
version was approved or why it changed. This skill builds the charter from the registers and points back to them,
records who approved it and when, and revises it only when an approved change requires it. The registers that the
charter introduces (initial risks, stakeholders, gates) are seeded from it, so the work is not typed twice.

## Use cases

### Draft the charter at kick-off

**Context:** Acme Portal has a project register, a budget register and a roadmap; risks and gates are still empty.

**Action:** Ask "draft the project charter".

**Result:** A charter with the milestones from the schedule register (the roadmap if there is none) and the budget from the register, questions on purpose,
objectives and authority, the critical reviewer's findings, then a numbered list of initial risks, stakeholders
and gates to add to the registers, written only for the ones you accept.

### Revise after a change

**Context:** Change request CR-004, approved last week, moves the payments module out of scope.

**Action:** Ask "update the project charter for CR-004" (Italian works too: the skill answers in your language).

**Result:** The scope changes shown side by side, a major version with `change: CR-004`, written after you agree.

## Usage

Ask in your own words ("project charter", "revise the charter") or run `/pm-skills:project-charter`.

## Inputs and outputs

- Reads `PROJECT.md`, `TAILORING.md`, the stakeholder, risk, decision, schedule, budget, RACI, gate and change
  registers, and the roadmap.
- Writes one charter in the folder of the project's Working documents section, named by
  `shared/scripts/doc_naming.py`, in the format of
  [`shared/documents/project-charter.md`](../../shared/documents/project-charter.md).
- On your confirmation, hands initial risks, stakeholders and gates off to `/pm-skills:risk-register`, `/pm-skills:stakeholder-register` and `/pm-skills:phase-gate-review`, which write them and report the IDs; the charter itself is the only file written here.
- Dispatches `pm-critical-reviewer` on the draft.

## Requirements

A project register (`/pm-skills:project-setup`) is recommended; without it the skill drafts in the session. The other registers are optional: what is missing is asked.

## Limitations

- Never marks the charter approved without your report of the approval.
- Writes no register: entries and changes to them go to the skills that keep each one.
- Revises an issued charter only through an approved change from the change log.
