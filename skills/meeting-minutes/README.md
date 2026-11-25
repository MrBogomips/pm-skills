---
summary: For project managers - turns meeting notes or a transcript into minutes with decisions, owned actions and risks, and records the decisions and new risks in the project's registers on request.
---

# meeting-minutes

Writes the minutes of a meeting from your notes, a transcript file, pasted text or the project's meeting tool: the
agenda, the discussion that led somewhere, the decisions, the actions with owner and due date, the risks raised and
the open questions. Once you approve the minutes, it proposes the decisions for the decision log and the new risks
for the risk register, and can turn the actions into work items.

## Why

Minutes are written late, read rarely and acted on even less, and the decisions in them never reach the decision log.
This skill condenses the meeting into what people who were not there need, insists on an owner and a date for every
action, and closes the loop: each decision and each new risk you accept becomes a register entry that links back to
the minutes, with its ID written in them.

## Use cases

### Minutes of a steering committee from a transcript

**Context:** The steering committee of Acme Portal met this morning; the transcript is in the meeting tool.

**Action:** Ask to "write the minutes of today's steering committee".

**Result:** A draft in the project's format and language, with inferred owners marked for you to confirm; after your
approval, a numbered list of proposed decision log entries and risk rows, and minutes written with their IDs.

### Actions from a sprint review into the backlog

**Context:** Your notes of the sprint review list five follow-ups; the project declares an issue tracker in write
mode.

**Action:** Ask "write the minutes of the meeting and create tasks for the actions".

**Result:** The minutes, then the five actions as an itemized list of work items; only those you confirm are created,
and their keys are added to the Actions table.

## Usage

Ask in your own words ("write the minutes", "minutes of yesterday's meeting", "action items from the meeting") or run
`/pm-skills:meeting-minutes`, with the notes pasted, a file path or the meeting's name.

## Inputs and outputs

- Reads `PROJECT.md` (naming, language, registers), the `meeting-minutes` section of `TAILORING.md`, and the source:
  pasted text, a file, or a tool with Purpose `meetings` in `TOOLS.md`.
- Writes the minutes in the folder of the project's Working documents section, named by
  `shared/scripts/doc_naming.py`, in the format of
  [`shared/documents/meeting-minutes.md`](../../shared/documents/meeting-minutes.md).
- Appends the entries you accept to `DECISIONS.md` and `RISKS.md` when the project declares them, and validates them.
- Creates work items only through an `issues` tool in Mode `write`, each one confirmed.

## Requirements

A project register (`/pm-skills:project-setup`); without it the skill can still draft minutes in the session.
Registers and tools are optional: what is not declared is skipped and named.

## Limitations

- Adds new decisions and new risks only; a decision that supersedes another or a change to a known risk is left to
  `/pm-skills:decision-log` and `/pm-skills:risk-register`.
- Does not send the minutes: use `/pm-skills:publish-deliverable`.
- Leaves out personal matters and opinions about people, even when the transcript has them.
