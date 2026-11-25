---
name: change-request
description: Keeps the project's change log (CHANGES.md) - raises a change request, assesses its impact on scope, schedule, cost and risk, has the analysis challenged, records who decided and when, marks it implemented. Use for a change to agreed scope, schedule or cost ("change request", "assess this change", "richiesta di modifica", "valuta l'impatto della modifica", "change log"); not for a decision alone.
---

# Change request

Keeps `CHANGES.md`: each change asked for, its impact on scope, schedule, cost and risk, who decided it and when, and
when it was implemented. It proposes the analysis; the user and the approvers the project names decide.

## Inputs

- **Project register**: `PROJECT.md`, declared in the project's `AGENTS.md` (or `CLAUDE.md`) as
  `- Project register: \`<path>\``. The log is its `- Change log: \`<path>\`` line under Registers. With no project
  register, suggest `/pm-skills:project-setup`; if the user wants to go on in the session, work on a path they name
  and invent no configuration.
- **Format**: `${CLAUDE_PLUGIN_ROOT}/shared/registers/changes.md`, the single source for keys, statuses and rules.
  Read it before writing; do not restate it to the user.
- **Tailoring**: the `## change-request` section of the tailoring register, when declared. Approval thresholds and
  approvers come only from its `rules`.
- **Other registers, read only**: risk register, decision log, team register, capacity register; formats in
  `${CLAUDE_PLUGIN_ROOT}/shared/registers/`. The Identity and Profile of `PROJECT.md` (contract type, planned end
  date, delivery approach, sprint length) frame the impact.
- **Tools** (from the tools register, by capability): `issues` (backlog, open work, velocity or throughput),
  `schedule` (milestones, baseline), `costs` (budget, rates per role), `releases`. Without a tools register, say
  which sources could not be read.

## Steps

1. **Start.** Read the project register, the log and the tailoring section. Say which tailoring rules apply; if
   there is no `rules` entry on approvals, say that the project names no approver and ask who decides.
2. **Set up** (no log, or the user asks): propose `CHANGES.md` at the project root (or where the Working documents
   section places registers) with the title only, and the line `- Change log: \`CHANGES.md\`` for the Registers
   section of `PROJECT.md`. Show both, write after the user agrees, then validate `PROJECT.md`:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/project_register.py" validate <path>`.
3. **Raise.** Take the request from the user's words, minutes, a ticket or a message. Ask only for what is missing
   among Requested by (a role, a body or a team slug), Description and Reason. Check open requests and accepted
   decisions on the same subject first; a duplicate is pointed out, not raised again. The ID is the highest `CR-`
   number in the file plus one, never reused; Raised is today unless the source dates it; Status `proposed`.
4. **Assess.** Work out each impact from facts, and say where each fact comes from:
   - **Scope**: deliverables, backlog items or requirements added, changed or dropped; acceptance and the
     Definition of Done when declared.
   - **Schedule**: effort against the team's capacity (capacity register, throughput or velocity from `issues`);
     milestones, releases or sprints moved (`schedule`). Use the user's estimates or ranges; never invent effort.
   - **Cost**: effort times rates per role from `costs`, other spend; whether it fits the contract type.
   - **Risk**: risks the change raises, removes or worsens in the risk register.

   Write `none` only when the facts show none; a gap is listed as a question, never filled with a guess. Add a
   Recommendation (approve, reject, defer, split) with its reason when the facts support one.
5. **Challenge** with `pm-critical-reviewer` before presenting the assessment as done. Give it the facts only: the
   draft section, its purpose and audience (the approvers), the register paths and the tool facts with their date.
   Fold its findings in or show them as open points.
   **Fable escalation**: when three or more impacts are not `none` (for example schedule, cost and risk), or the
   assessment goes to a steering committee or the client, dispatch the reviewer with the model set to `fable`;
   tell the user before dispatching, and why.
6. **Write the assessment**: the four impacts, the Recommendation if any, Status `assessed`. Name the approvers
   the `rules` require for this change (for example a threshold of days or cost) and why; with no rule, the
   approver is whoever the user names.
7. **Record the decision** only when the user reports it: Status `approved` or `rejected`, `Decided by` (the role,
   body or slug that decided, never inferred), `Decided on` (the day it was taken). If a `rules` entry requires an
   approver who is not the one named, say so and do not mark it approved. Then offer a decision log entry:
   suggest `/pm-skills:decision-log`, or, if the user agrees, append the entry here following
   `${CLAUDE_PLUGIN_ROOT}/shared/registers/decisions.md` (next free `D-NNN` from the file, `Source` the change
   log), then add `Decision: D-NNN` to the request. A `Decision` always names an entry that exists in the log.
   When an approved change alters scope, also suggest revising the issued charter (`/pm-skills:project-charter`)
   and the WBS (`/pm-skills:wbs-builder`).
8. **Propose risks** the impact creates, as cause, event and effect, with Probability and Impact on the risk
   register's `Scale`. Suggest `/pm-skills:risk-register`, or append the rows the user accepts with the next free
   `R-NNN`; `Strategy`, `Owner` and `Review` come from the user, never made up. Changes to existing risks go to
   `/pm-skills:risk-register`.
9. **Withdraw or implement.** `withdrawn` when the requester drops it. `implemented` only for an approved request,
   with `Implemented on`, when the user or the tools show the work done (merged, released, delivered).
10. **Validate** after every write, fixing until each exits 0:
    `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/changes_register.py" validate <path>`, and
    `decisions_register.py` or `risks_register.py` when those were written.

## Always

- **Show before writing**: every change to `CHANGES.md`, `DECISIONS.md`, `RISKS.md` or `PROJECT.md` is shown first
  and written after the user agrees; one write per register change.
- **Facts apart from inferences**: say what was read, what was inferred, which estimates came from the user and
  which sources were unavailable.
- **People**: requesters and deciders as roles, bodies or slugs; no contacts, no judgment of anyone.
- Talk and write values in the user's language, or the project's `Deliverable language`; keys stay in English.

## Never

- Never invent an approver, a threshold, an estimate or a rate; never mark a request approved without the decision
  reported by the user.
- Never delete, renumber or rewrite a request after its decision.
- Never edit existing decisions or risks here, or write any external system.
- Never apply a tailoring rule that loosens a guardrail; say that it was ignored and why.

## Extension points

- `rules`: approval thresholds (days, cost, scope) and the approvers for each, checks required before assessing or
  deciding.
- `steps`: extra steps before assessing, before recording a decision, or after implementing.
- `terms`: the project's words for change requests, bodies and statuses in conversation.
