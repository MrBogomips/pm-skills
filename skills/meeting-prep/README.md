---
summary: For project managers - guides the preparation of a steering, client or any meeting from the registers and previous minutes, writing a brief with agenda, decisions sought and pre-reads.
---

# meeting-prep

Guides you through the preparation of a meeting, one question at a time. It reviews what the registers hold that
matters for it (actions due, decisions pending, high risks, change requests, gates, open questions), asks for the
objective, attendees, agenda items and pre-reads, then writes a meeting brief.

## Why

Meetings go badly when the project manager arrives without knowing what is overdue, what must be decided and who
needs what beforehand. The facts are scattered over the registers and the last minutes. This skill gathers them,
asks for the few choices only you can make, and leaves a brief where every item has a decision sought or says it is
information only. It writes no register: what it finds goes to the keepers, and your own preparation tasks to the
action log.

## Use cases

### Prepare the steering committee

**Context:** The Acme Portal steering committee meets on Thursday; last time two actions and a change request were
left open.

**Action:** Ask "prepare the steering committee".

**Result:** The open items with their IDs, questions for the objective, agenda and pre-reads, and a draft brief with
a decision sought per item.

### Prepare a client meeting

**Context:** A review with Acme Corp is on the calendar; the communication plan lists it as monthly.

**Action:** Ask "agenda for the client meeting".

**Result:** The cadence and participants from the plan as defaults, the stakeholders involved by role and level, and
a brief with the pre-reads to send and by when.

## Usage

Ask in your own words ("prepare the meeting", "meeting brief", "pre-read for the steering") or run
`/pm-skills:meeting-prep`, with the kind and date of the meeting if you know them.

## Inputs and outputs

- Reads `PROJECT.md`, the registers it declares (actions, decisions, risks, changes, gates, stakeholders), the
  previous minutes, the communication plan and `TAILORING.md`.
- Writes one meeting brief in the folder of the project's Working documents section, named by
  `shared/scripts/doc_naming.py`, in the format of
  [`shared/documents/meeting-brief.md`](../../shared/documents/meeting-brief.md).
- Hands off new register entries and your preparation tasks to their keepers, on your agreement.

## Requirements

A project register (`/pm-skills:project-setup`). Registers and documents are optional: what is missing is named in
the report. The open actions need the action log (`/pm-skills:action-log`).

## Limitations

- Writes no register; it hands off.
- Does not send the brief or the pre-reads: use `/pm-skills:publish-deliverable`. The brief holds your position, so
  it is internal.
- Holds roles and levels of stakeholders, never contacts.
