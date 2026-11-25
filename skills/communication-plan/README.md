---
summary: For project managers - drafts the communication plan from the stakeholder register, the RACI matrix and the reporting cadence, and flags stakeholders the project depends on who receive nothing.
---

# communication-plan

Drafts the project's communication plan: audiences, what each receives, when, through which channel, who owns it and
which report or meeting produces it, plus the meetings and the escalation path.

## Why

Communication plans are usually written once and never checked against the people they are for: the sponsor gets
three overlapping reports while the security office, whose sign-off the go-live needs, hears nothing. This skill
starts from the stakeholder register and the RACI matrix, ties each communication to the document that produces it,
and points out who is left out.

## Use cases

### Draft the plan

**Context:** Acme Portal has a stakeholder register with five active entries and a biweekly reporting cadence.

**Action:** Ask "draft the communication plan".

**Result:** Audiences by role with their register IDs, the status report every two weeks to the steering committee,
the sprint review for the product owner and end users, the meetings and the escalation path, and a warning that the
security office, below its desired engagement, receives nothing.

### Check it after the register changed

**Context:** Two stakeholders were added after the last steering meeting.

**Action:** Ask "aggiorna il piano di comunicazione".

**Result:** A revision with the new audiences, shown before it is written.

## Usage

Ask in your own words ("communication plan", "piano di comunicazione") or run `/pm-skills:communication-plan`.

## Inputs and outputs

- Reads `PROJECT.md`, `TAILORING.md`, `STAKEHOLDERS.md`, `RACI.md`, `GATES.md`, the charter, the earlier plan and
  the `publish` and `meetings` tools through `TOOLS.md`.
- Writes one communication plan in the folder of the project's Working documents section, named by
  `shared/scripts/doc_naming.py`, in the format of
  [`shared/documents/communication-plan.md`](../../shared/documents/communication-plan.md).

## Requirements

A project register (`/pm-skills:project-setup`). A stakeholder register makes the plan complete; without one the
skill asks for the audiences.

## Limitations

- Holds no personal contacts: channels name the means, the address lives in the systems that own it.
- Does not change the stakeholder register; it suggests `/pm-skills:stakeholder-register` when an entry needs it.
- Does not send anything: distribution is `publish-deliverable`'s job.
