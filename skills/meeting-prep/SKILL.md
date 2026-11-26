---
name: meeting-prep
description: Guides the project manager step by step through preparing a meeting - steering committee, client meeting or any other - from the registers, open points and previous minutes, and writes a meeting brief with agenda, decisions sought and pre-reads. Use for "prepare the meeting", "agenda for the steering", "meeting brief", "pre-read".
---

# Meeting prep

Walks the project manager through the preparation of a meeting: what is open, who is in the room, what each agenda
item must decide, what to send beforehand. Produces a meeting brief; changes no register.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **The project register**: `PROJECT.md`, declared by `` - Project register: `PROJECT.md` `` in the project's
  `AGENTS.md` (or `CLAUDE.md`): code, `Deliverable language`, naming Conventions and Registers. With none, suggest
  `/pm-skills:project-setup`; you may still prepare in the session, inventing no configuration.
- **Registers**, those declared, read only: actions (`ACTIONS.md`), decisions, risks, changes, gates, stakeholders
  (roles and levels, never contacts). For the open actions you may run
  `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/pm_backlog.py" --project <PROJECT.md>`: the PM backlog view of
  `action-log`.
- **Documents**: the previous minutes of the same kind of meeting (their Actions and Open questions), and the
  communication plan, when it exists: the meeting's row gives its kind, cadence, participants and record.
- **Formats**: `${CLAUDE_PLUGIN_ROOT}/shared/documents/meeting-brief.md`,
  `${CLAUDE_PLUGIN_ROOT}/shared/documents/meetings.md` and `${CLAUDE_PLUGIN_ROOT}/shared/documents/common.md`;
  hand-offs follow `${CLAUDE_PLUGIN_ROOT}/shared/handoff.md`.
- **Tailoring**: the `## meeting-prep` section of `TAILORING.md`, when declared.

## Steps

1. **Read the configuration** and the tailoring section; say which rules you will apply and which registers you
   could not read.
2. **Identify the meeting**: kind and date. When the communication plan has a row for it, propose its cadence,
   participants and record as defaults; otherwise ask.
3. **Review what is open**, by register, in one list with IDs: actions due or overdue; decisions pending or taken
   since the previous meeting; risks high or due for review; change requests to decide; gates near; the previous
   minutes' open questions. Mark what you inferred. Say which registers are missing.
4. **Ask one step at a time**, proposing a default from step 3 and waiting for the answer:
   objective and the outcome that makes the meeting a success; attendees and the stakeholders involved; agenda items,
   each with time, owner and the decision sought; which open items go to which item; pre-reads, to whom, by when.
5. **Draft the brief** in the format: a short content brief per item (facts, position, expected questions), the
   open items with their IDs, the times adding up to the meeting's length.
6. **Name the file** from the folder of the project's Working documents section (ask once if none) with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/doc_naming.py" next --project <PROJECT.md> --dir <folder> --type meeting-brief --date <meeting date> [--slug <slug>]`.
   Exit status 3: give a slug, or revise the existing brief.
7. **Show the brief and the path**; write it, `status: draft`, only after the user agrees.
8. **Hand off** what you found that a register should hold (a risk, a decision to record, a change request) and the
   preparation tasks for the project manager ("send the pre-read by Friday") as proposals to the keeper, the
   tasks to `/pm-skills:action-log`, as `shared/handoff.md` says.
9. **Report** what you read, inferred and could not read, and what was handed off; suggest
   `/pm-skills:meeting-minutes` after the meeting, with the brief as input.

## Always

- One question at a time; propose, never presume an answer.
- Every agenda item gets a decision sought, or `information only`.
- Open items carry their register IDs, as they stand on the day.
- Roles and levels for stakeholders; work names for attendees.
- Show before writing.

## Never

- Never write, append to or edit a register: hand off to its keeper.
- Never put contacts, sensitive personal data or evaluations of people in the brief.
- Never run a keeper without the user's agreement on the proposals.
- Never send the brief or the pre-reads: distribution is `/pm-skills:publish-deliverable`'s job, on request.

## Extension points

- `format`: sections added to the brief, a template per kind of meeting, extra kinds.
- `scale`: the length and time slots of a kind of meeting.
- `rules`: extra checks, such as a pre-read sent a number of days before.
- `steps`: extra steps before the review, before drafting, or after the brief.
- `terms`: the project's words for the brief and its parts.
