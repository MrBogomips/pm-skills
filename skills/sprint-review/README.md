---
summary: For Scrum teams and their project managers - drafts the sprint review, with what was delivered against the Sprint Goal and the Definition of Done, what was not and why, the stakeholders' feedback and the backlog changes it leads to.
---

# sprint-review

Drafts the sprint review: the Sprint Goal and whether it was met, the items delivered with the evidence that they
meet the Definition of Done, the items not delivered and why, the stakeholders' feedback and the proposed Product
Backlog adaptations. The facts come from the issues tool and the `project-activity-scout` agent; the feedback from
your notes or the meeting tool.

## Why

A review that lists every ticket closed hides the ones that are done in the tracker but not releasable, and the
feedback heard in the room is lost by the next planning. This skill counts an item as delivered only on evidence
against the Definition of Done, states why the rest was not delivered as facts, records the feedback by role and
turns it into proposed backlog changes, and points new risks and decisions to their registers.

## Use cases

### Prepare the review before the meeting

**Context:** Sprint 14 of Acme Portal ends today; its plan holds the Sprint Goal.

**Action:** Ask "prepare the sprint review".

**Result:** A draft with Delivered and Not delivered filled from the facts, the goal judged with its reasons, and
Feedback left for after the meeting.

### Record the stakeholders' feedback

**Context:** After the review you paste your notes: the sponsor wants the export in CSV, end users found the search
slow.

**Action:** Ask "add the feedback to the sprint review".

**Result:** Feedback by role, two proposed backlog items tied to it, and, on a fixed-price contract, a suggestion to
run `/pm-skills:change-request` for the new export.

## Usage

Ask in your own words ("sprint review", "what did the sprint deliver") or run `/pm-skills:sprint-review`. Give the notes or
minutes of the meeting when you have them.

## Inputs and outputs

- Reads `PROJECT.md` (framework, Definition of Done, contract type, naming, language, registers), `TAILORING.md`,
  `RISKS.md`, `DECISIONS.md`, `STAKEHOLDERS.md`, the sprint plan, your notes or the meeting tool, and the project's
  tools through `TOOLS.md`.
- Writes one review in the folder of the project's Working documents section, named by
  `shared/scripts/doc_naming.py`, in the format of
  [`shared/documents/sprint-review.md`](../../shared/documents/sprint-review.md).
- On request, creates the accepted backlog items through an issues tool declared with Mode `write`, after you
  confirm the itemized list.

## Requirements

A project register (`/pm-skills:project-setup`) and a tools register with an `issues` tool. The
`project-activity-scout` agent ships with the plugin.

## Limitations

- Done-ness is judged on what the tools show; a missing Definition of Done file narrows it to the tracker's state.
- Never records risks or decisions itself: it hands proposals to `/pm-skills:risk-register` and `/pm-skills:decision-log`.
- Never sends the review: use `/pm-skills:publish-deliverable`.
