---
title: Meetings from brief to minutes
area: stakeholders
type: operational
---

# Meetings from brief to minutes

The meeting cycle has four steps: prepare, hold, record, distribute. The plugin helps with the first, third and
fourth; you hold the meeting.

## 1. Prepare: `meeting-prep`

Ask "prepare the steering committee on 2026-11-24". The skill reviews what is open in the registers, with IDs:
actions due or overdue, decisions pending or taken since the last meeting, risks that are high or due for review,
change requests to decide, gates that are near, and the open questions of the previous minutes. It says which
registers it could not read.

It then asks one question at a time, proposing a default for each: the objective and what would make the meeting a
success, the attendees, the agenda items (each with time, owner and the decision sought), which open items belong to
which item, and the pre-reads (to whom, by when). If the project has a communication plan with a row for this kind
of meeting, its cadence and participants are the defaults.

The result is a **meeting brief**, written as a draft once you agree. It has these headings: Objective, Attendees,
Agenda, Content brief, Open items and Pre-reads. Every agenda item has a decision sought, or says `information
only`. The brief is for you: it may hold your position and the objections you expect, so it is not distributed as
it is. Preparation changes no register; what it finds that a register should hold goes to the keeper as a handoff
proposal, and your preparation tasks ("send the pre-read by Friday") go to `action-log`.

## 2. Hold the meeting

Take notes, or let a tool record. Transcription and translation are out of scope for the plugin: your own tools or
skills do them, registered in `TOOLS.md`, and their output is the source for the minutes.

## 3. Record: `meeting-minutes`

Give the skill the source in whatever form you have it:

- notes you paste;
- a transcript, or any file, including one in the project's inbox (see [The inbox](inbox.md));
- a meeting tool registered in `TOOLS.md` with the purpose `meetings`;
- minutes written by someone else. These are **imported**: the skill keeps their text, extracts decisions and
  actions from them and rewrites nothing.

If the meeting had a brief, the minutes inherit its agenda and attendees and record its path. The minutes have
these headings: Agenda, Discussion, Decisions, Actions, Risks raised, Open questions and Internal notes. Discussion
is not a transcript: it keeps the points that lead to a decision or an action. Every action needs an owner and a
due date; when the source gives neither, the skill asks, or moves it to Open questions. Anything it inferred is
marked and you confirm it. You correct the draft until you approve the content.

Minutes record facts, not opinions about the people who spoke, and leave out personal matters raised in the meeting
and contacts.

### Handoffs

After you approve the content, the skill proposes, as a numbered list, what the registers should hold. It proposes
only for registers the project declares:

| Found in the meeting | Goes to |
|---|---|
| a decision | `decision-log` |
| a risk, or a change to a known one | `risk-register` |
| a change request | `change-request` |
| an action | `action-log` |

You accept all, some or none. After each keeper writes, it reports the IDs (`D-004`, `R-007`, `CR-003`, `AC-021`),
and the skill puts them in the minutes under Decisions, Actions, Risks raised and Open questions. A declined
proposal is not recorded; if you want a trace, it goes under Internal notes.

### A change request raised in the meeting

For each change request raised, you choose one of four ways:

1. **Record it as proposed**, to be assessed later.
2. **Assess it now**, with `change-request`.
3. **Record it and reject it at once**; `change-request` asks who has the authority to reject.
4. **Do not record it.** Then it appears only under Internal notes.

### Internal notes

Internal notes is the last heading of the minutes: notes for internal use only, such as a change request you chose
not to record, a reservation about a decision, or context the client should not read. Everything above that
heading is written so that it can be distributed.

## 4. Distribute: `publish-deliverable`

Ask "export the minutes to Word" or "send the minutes". The skill renders the Markdown through the renderer the
project declares in `TOOLS.md` (a tool with the purpose `publish` whose scope maps a document type to a format) and
always removes the Internal notes section from what it renders or sends, never from the Markdown source. If the
minutes are still a draft, it asks you to confirm. It sends or uploads only through a tool declared `write`, showing
exactly what goes where and waiting for your confirmation. If no renderer is declared, it proposes one to reuse
and offers to add it to `TOOLS.md`.

Neither `meeting-prep` nor `meeting-minutes` sends anything.

## At a glance

| Step | Skill | Output | Written to the registers by |
|---|---|---|---|
| Prepare | `meeting-prep` | meeting brief (draft) | nobody: handoffs only |
| Record | `meeting-minutes` | minutes with IDs | `decision-log`, `risk-register`, `change-request`, `action-log` |
| Distribute | `publish-deliverable` | Word, PDF, email or other, without Internal notes | not applicable |
