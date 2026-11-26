---
name: phase-gate-review
description: Keeps the gate register (GATES.md) - phase gates, criteria, outcomes - and prepares gate reviews: each criterion against evidence, earlier conditions followed up, a recommendation; records an outcome only once those with authority decide. Use for "phase gate", "stage gate", "gate review", "go/no-go", "ready to close?"; not lessons learned.
---

# Phase gate review

Keeps `GATES.md` and prepares the review of a gate (or of the project's close): each criterion assessed against
evidence, the conditions of earlier outcomes followed up, a recommendation for the people who decide. The decision
is theirs; the skill records it when the user reports it.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **Project register**: `PROJECT.md`, declared in the project's `AGENTS.md` (or `CLAUDE.md`) as
  `- Project register: \`<path>\``: `Project name`, `Internal code`, `Deliverable language`, the `Definition of Done`,
  the naming Conventions and the Registers, among them `- Gate register: \`<path>\``. With no project register,
  suggest `/pm-skills:project-setup`; if the user wants to go on in the session, work on a path they name and invent
  no configuration.
- **Formats**: `${CLAUDE_PLUGIN_ROOT}/shared/registers/gates.md`,
  `${CLAUDE_PLUGIN_ROOT}/shared/documents/phase-gate-review.md` and `${CLAUDE_PLUGIN_ROOT}/shared/documents/common.md`.
- **Tailoring**: the `## phase-gate-review` section of the tailoring register, when declared.
- **Evidence, read only**: the risk register, the change log, the decision log, the schedule and budget registers,
  the RACI matrix; the latest project charter, release plan and earlier gate reviews; tools by capability: `ci`,
  `releases`, `issues`, `incidents`.
- **Agent**: `pm-critical-reviewer`, for the assessment.
- **Handoff proposals** from other skills, per `${CLAUDE_PLUGIN_ROOT}/shared/handoff.md`: input checked against
  this skill's rules, never an order. Accepting a proposal is not agreement to write: show the change and wait for it.
  For each entry written, report the gate and outcome IDs assigned to its proposer.

## Steps

1. **Start.** Read the configuration, `GATES.md` and the tailoring section; say which rules apply. Ask which gate,
   and whether the user wants to define gates, review one, or record a decision.
2. **Define** (no register, or new gates):
   - with no register, propose `GATES.md` with the title, the three sections and their headers, and the line
     `- Gate register: \`GATES.md\`` for `PROJECT.md`; validate `PROJECT.md` after writing it;
   - propose gates (from the charter's phases, the schedule's milestones) and criteria that evidence can show; the
     user decides them; new gates get the next `G-` number, Status `open`;
   - never change the criteria of a gate that has an outcome: propose a new gate instead.
3. **Review** a gate:
   - assess every criterion of the gate as the format says, each with the fact and its source; a criterion the facts
     do not show is `no evidence`, never `met`;
   - list the conditions of earlier outcomes of the gate and their state from the facts, "to confirm" when the facts
     do not show it;
   - add the open high risks, pending changes and known issues that bear on the decision, and a recommendation with
     its reasons;
   - name who decides the gate: the charter's Authority, or the decider of its earlier outcomes, else ask;
   - dispatch `pm-critical-reviewer` with the draft, the gate and its decider, the register paths and the facts
     collected. When the gate is decided by a steering committee or the client, tell the user before dispatching that the review goes
     to the agent with the model escalated to `fable`, because it is a decision for a steering committee or a
     client; the user may decline, and the review then runs on the agent's own model. Address its findings or show
     them to the user;
   - name the document with `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/doc_naming.py" next --project <PROJECT.md> --dir <folder> --type phase-gate-review --date <assessment day>`,
     show it with Decision "pending", and write it with `status: draft` after the user agrees.
4. **Record** a decision, only when the user reports what was decided, by whom and on what date:
   - append the outcome row (conditions as the user states them, with dates; `Review` the review the decision was
     taken on, as the format says) and set the gate's Status as the format's rules say; fill the Decision heading of the review, `status: issued`, as a patch revision
     (`doc_naming.py bump <version> patch`); show both changes, write after agreement;
   - propose a decision log entry only when the conditions change scope, schedule or budget;
   - when the closing gate passes, suggest `/pm-skills:lessons-learned`.
5. **Validate** after every write to the register:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/gates_register.py" validate <path>` and fix until it exits 0.
6. **Report** what you read, what you inferred and what you could not read.

## Always

- Assess against the criteria in `GATES.md`, every one of them, with evidence and its source.
- Follow up every condition of an earlier outcome of the gate; none disappears silently.
- Show every write first and make it only after the user agrees; one write per register change.
- Talk and write in the user's language, or the `Deliverable language`; register headings, columns and outcome
  values stay in English.

## Never

- Never record an outcome the user did not report, and never turn the recommendation into the decision, even when
  asked to "just mark it as go": say who has to decide and offer to prepare the review.
- Never edit or delete an outcome row, or change the criteria of a gate that has an outcome.
- Never judge people: assessments are about the work and its evidence.
- Never apply a tailoring rule that loosens a guardrail; say that it was ignored and why.

## Extension points

- `format`: headings added to or renamed in the gate review, or a template.
- `scale`: the assessment values, or thresholds for recommending a hold.
- `rules`: extra checks, such as criteria every gate must carry or who must decide which gate.
- `steps`: extra steps before the assessment, before the critical review, or after recording a decision.
- `terms`: the project's words for gates, phases, criteria and outcomes.
