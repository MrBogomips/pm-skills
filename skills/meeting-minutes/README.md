---
summary: For project managers - turns notes, a transcript or others' minutes into minutes with decisions, actions, risks and change requests, handed to the registers' keepers.
---

# meeting-minutes

Writes the minutes of a meeting from your notes, a transcript file, an inbox file, pasted text or the project's
meeting tool, or imports minutes written by others without rewriting them. It extracts the decisions, actions with
owner and due date, risks and change requests, and hands them to the keepers of the registers.

## Why

Minutes are written late, read rarely and acted on even less, and the decisions in them never reach the decision log.
This skill condenses the meeting into what people who were not there need, insists on an owner and a date for every
action, and closes the loop: what you accept goes to the keeper of the register, which reports the ID that is then
written in the minutes. Minutes are not a register of their own: the keepers write the registers.

## Use cases

### Minutes of a steering committee from a transcript

**Context:** The steering committee of Acme Portal met this morning; the transcript is in the meeting tool.

**Action:** Ask to "write the minutes of today's steering committee".

**Result:** A draft in the project's format and language, with inferred owners marked for you to confirm; after your
approval, a numbered list of proposed decision log entries and risk rows, and minutes written with their IDs.

### Change requests raised in a meeting

**Context:** The client asked for two changes in the meeting; the project manager wants one assessed later and the
other kept only for internal reference.

**Action:** Ask "write the minutes of the client meeting".

**Result:** For each change request you choose: hand off as proposed, assess now, record and reject, or keep it only
under Internal notes, which `/pm-skills:publish-deliverable` removes before the minutes go out.

## Usage

Ask in your own words ("write the minutes", "minutes of yesterday's meeting", "action items from the meeting") or run
`/pm-skills:meeting-minutes`, with the notes pasted, a file path or the meeting's name. If you prepared the meeting
with `/pm-skills:meeting-prep`, the brief is picked up.

## Inputs and outputs

- Reads `PROJECT.md` (naming, language, registers), the `meeting-minutes` section of `TAILORING.md`, the meeting
  brief when there is one, and the source: pasted text, a file (also from the inbox), or a tool with Purpose
  `meetings` in `TOOLS.md`.
- Writes the minutes in the folder of the project's Working documents section, named by
  `shared/scripts/doc_naming.py`, in the format of
  [`shared/documents/meeting-minutes.md`](../../shared/documents/meeting-minutes.md), ending with `Internal notes`.
- Writes no register: proposes decisions, risks, change requests and actions to their keepers and records the IDs.

## Requirements

A project register (`/pm-skills:project-setup`); without it the skill can still draft minutes in the session.
Registers are optional: for those not declared no hand-off is proposed, and the report names them.

## Limitations

- Does not transcribe, translate or extract transcripts: your registered tools or skills do, and their output is the
  source.
- Creates no work items: `/pm-skills:action-log` does, when an issues tool is declared in write mode.
- Does not send the minutes: use `/pm-skills:publish-deliverable`.
- Leaves out personal matters and opinions about people, even when the transcript has them.
