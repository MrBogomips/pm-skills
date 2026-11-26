---
summary: For project managers - sorts the files that land in the project's inbox folder, says what each one is and which skill should process it, then files it and hands it over once you agree.
---

# inbox-triage

Reads the files waiting in the project's inbox folder (minutes written by others, transcripts from external tools,
saved emails, requests, documents), classifies each one, proposes the skill that should process it and, on your
confirmation, moves it to its final location and hands it to that skill, one file at a time.

## Why

Material arrives faster than a project manager can sort it: a transcript here, a client's request there, minutes from a
colleague. Without a routine it sits in a folder, and the decisions, risks and actions inside it never reach the
registers. This skill makes the first pass cheap and safe: one table of what each file is and where it should go,
your decision on each row, and no register touched except through its own keeper.

## Use cases

### Monday morning inbox

**Context:** Five files landed in `inbox/` over the week: a transcript of the Acme Portal steering committee, a client
email asking for dark mode, a signed contract, a screenshot and a recording.

**Action:** Ask to "triage the inbox".

**Result:** A table with the route of each file (`meeting-minutes`, `change-request`, file only, leave, needs an
external transcription tool); after you confirm, the files are moved and the first hand-off starts.

### Inbox with no declared folder

**Context:** The project's instruction file has no Working documents section.

**Action:** Ask "what's in the inbox".

**Result:** The skill asks once where incoming material lands, suggests recording it, and lists that folder; it never
creates one.

## Usage

Ask in your own words ("triage the inbox", "process the inbox", "sort incoming documents") or run
`/pm-skills:inbox-triage`.

## Inputs and outputs

- Reads `PROJECT.md` (declared registers), the Working documents section of the project's instruction file (inbox
  and destinations), the `inbox-triage` section of `TAILORING.md`, and the files of the inbox.
- Moves the files you confirm to their destinations and hands them off per
  [`shared/handoff.md`](../../shared/handoff.md); registers are written only by their keepers.

## Requirements

A project register (`/pm-skills:project-setup`) to know which routes exist; without it the skill still classifies. The
inbox folder is the project's own. Audio and video need an external transcription tool.

## Limitations

- Only routes: no extraction, transcription or translation; those belong to tools or skills the project declares.
- Never deletes a file and never overwrites one at the destination.
- Reads a file only far enough to classify it; unclear files stay in the inbox with the reason.
