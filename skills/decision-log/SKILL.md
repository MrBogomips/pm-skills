---
name: decision-log
description: Keeps the project decision log (DECISIONS.md): records a decision with context, options and who took it, supersedes or revokes it without rewriting history, and answers what was decided and why. Use to record or look up a single decision ("record a decision", "what did we decide about", "why did we decide", "decision log"); not for whole-meeting minutes.
---

# Decision log

Keeps `DECISIONS.md`: the decisions that shape the project, with their context, the options considered and who took
them, so later work can rely on them and later readers know why.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **Project register**: `PROJECT.md`, declared in the project's `AGENTS.md` (or `CLAUDE.md`) as
  `- Project register: \`<path>\``. The log is its `- Decision log: \`<path>\`` line under Registers. With no
  project register, suggest `/pm-skills:project-setup`; if the user wants to go on in the session, work on a path
  they name and invent no configuration.
- **Format**: `${CLAUDE_PLUGIN_ROOT}/shared/registers/decisions.md`, the single source for keys, statuses and rules.
  Read it before writing; do not restate it to the user.
- **Tailoring**: the `## decision-log` section of the tailoring register, when declared.
- **Team register**, read only: slugs for `Decided by`.
- **Tools** (from the tools register, by capability), only to read a source the user points to: `meetings`,
  `messages`, `documents`, `issues`.

## Steps

1. **Start.** Read the project register, the log and the tailoring section. Say which tailoring rules apply.
2. **Set up** (no log, or the user asks):
   - propose `DECISIONS.md` at the project root (or where the Working documents section places registers), with the
     title only;
   - propose the line `- Decision log: \`DECISIONS.md\`` for the Registers section of `PROJECT.md`;
   - show both, write after the user agrees, then validate `PROJECT.md` too:
     `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/project_register.py" validate <path>`.
3. **Record a decision.**
   - Take what the user gives (their words, minutes, a thread, a ticket) and ask only for the required keys still
     missing: Date, Decided by, Context, Decision. Offer Options, Consequences and Source when the material holds
     them; do not insist.
   - Only a decision taken goes in. If the material shows a discussion, a proposal or a preference with no one
     deciding, say so and record nothing; offer to record it once it is decided.
   - `Decided by` is who took it (a role, a body, a team register slug), never inferred from who spoke most; "we"
     is not enough: ask. The Date is the day it was taken, not today unless it was taken today.
   - Before writing, look for accepted decisions on the same subject: a conflict means the new one supersedes the
     old (step 4) or it is not a decision yet. Ask.
   - The ID is the highest `D-` number in the file plus one, three digits at least; never reuse one. Status is
     `accepted`. The title is a short noun phrase for the decision.
4. **Supersede or revoke.** An accepted decision is never rewritten or deleted.
   - Supersede: record the new decision with `Supersedes: D-NNN`; on the old one change only `Status` to
     `superseded` and add `Superseded by:` the new ID. Both in one write.
   - Revoke: change only `Status` to `revoked`. If the user wants the reason and who withdrew it on record, also
     record a new decision whose Decision is the withdrawal and whose Context names the revoked ID, with no
     `Supersedes` link (nothing replaces it).
   - A fix of form (a typo, a broken Source path) is allowed when shown and agreed; anything that changes the
     meaning is a new decision.
5. **Find decisions** ("what did we decide about X", "why did we pick X"). Search titles, Context, Decision, Options
   and Consequences. Answer with the decision in force, its ID, date, who decided and why; follow `Superseded by`
   to the current one and mention the history when it matters. Quote the log; when nothing matches, say so and
   do not answer from memory or guesswork.
6. **Propose risks.** When a decision's consequences carry uncertainty (a new dependency, a deadline, a cost that
   may grow), state the candidate risk as cause, event and effect and suggest `/pm-skills:risk-register` to assess
   it. Do not write the risk register.
7. **Validate** after every write:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/decisions_register.py" validate <path>` and fix until it exits 0.

## Always

- **Show before writing**: every change to `DECISIONS.md` or `PROJECT.md` is shown first and written after the user
  agrees.
- **One write per change**: a supersession, with both entries, is a single edit.
- **Facts apart from inferences**: say what was taken from the source, what was inferred and which sources could
  not be read.
- **People**: no contacts and no judgment of a person in any entry.
- Talk and write values in the user's language, or the project's `Deliverable language`; headings and keys stay in
  English.

## Never

- Never record as decided what was only discussed or proposed.
- Never change an accepted decision's content, delete an entry or renumber IDs.
- Never write the risk register or any external system.
- Never apply a tailoring rule that loosens a guardrail; say that it was ignored and why.

## Extension points

- `rules`: extra checks, for example who may decide what, or decisions that need a named approver.
- `steps`: extra steps before recording a decision, for example linking the ticket that tracks its work.
- `terms`: the project's words for decisions, bodies and roles in conversation.
