# Scenarios: project-charter

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **registers**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md`, with `BUDGET.md`, `SCHEDULE.md`, `STAKEHOLDERS.md`, `DECISIONS.md` and `CHANGES.md` from
  `tests/fixtures/`; `RISKS.md` with the header only; `GATES.md` with empty tables; a `product-roadmap/` document.
- **issued**: **registers**, plus an issued charter `ACME-PC-001.md` (`version: 1.0.0`) and an approved change
  CR-004 in `CHANGES.md` that moves the payments module out of scope.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| draft-from-registers | registers | "Draft the project charter" | Milestones from the schedule, budget and reserves from BUDGET.md, stakeholders as roles pointing to the register; Sources lists what was read; `status: draft` |
| missing-authority-asked | registers | "Draft the charter" | Asks for purpose, objectives with success criteria, out of scope and authority instead of inventing them |
| critic-fable-for-client | registers | "Draft the charter for the client's approval" | Tells the user the review goes to `pm-critical-reviewer` escalated to `fable` and why; offers to decline; shows the findings |
| proposes-register-rows | registers | "Draft the charter and seed the registers" | One numbered list of new risks (`R-001`...), stakeholders (next `S-` IDs) and gates with criteria; asks for required values it lacks; writes only accepted rows; each register validates; SCHEDULE.md untouched |
| issue-with-approval | registers, a draft written | "The sponsor approved the charter today" | Sets `status: issued`, `approved-by`, `approved-on`, fills Approval; never before the user reports it |
| revise-needs-change | issued | "Aggiorna la carta del progetto: rimuovi il modulo pagamenti dallo scope" | Finds CR-004 approved; shows the differences; major version with `change: CR-004`; without an approved change it suggests `/pm-skills:change-request` |
| no-project-register | no project | "Write the project charter" | Suggests `/pm-skills:project-setup`; drafts in the session only if the user wants, asking for the facts; invents no configuration |
| risks-stakeholders-gates-as-handoffs | registers | "Write the charter and put the initial risks, stakeholders and gates in the registers" | Writes only the charter; prepares handoff proposals to `/pm-skills:risk-register`, `/pm-skills:stakeholder-register` and `/pm-skills:phase-gate-review` with no IDs; hands off only those the user accepts, one keeper at a time; reports the IDs the keepers assign; edits no register itself |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.3.0 | revise-needs-change (headless, sonnet, writes disallowed; no approved CR in the fixture) | pass | Refused the revision without an approved change; suggested change-request; named the major bump and the WBS impact |
| 2026-11-25 | 1.3.1 | draft-from-registers, missing-authority-asked, critic-fable-for-client, proposes-register-rows, issue-with-approval, revise-needs-change (with approved CR), no-project-register (headless, writes disallowed) | draft-from-registers pass; missing-authority-asked pass; critic-fable-for-client pass; proposes-register-rows pass; issue-with-approval pass; revise-needs-change partial; no-project-register pass | Charter inputs supplied in the prompt for critic-fable-for-client (review run on the escalated model, findings shown) and proposes-register-rows (numbered R-/S-/G- list, required values asked, nothing written); without them the first turn asks for the missing inputs first. revise-needs-change: with the prompt 'Rimuovi il modulo pagamenti dallo scope' the change-request skill answered (CR already approved, follow-ups) and the charter was not revised; with 'Revise the project charter ... remove the payments module' it passed (CR cited, major bump, change key, differences shown) |
| 2026-11-25 | 1.3.1 | revise-needs-change with the original Italian prompt (re-run after fixes, headless, writes disallowed) | partial | Still answered from the change log: CR approved, follow-ups listed, and revising the charter and WBS suggested as next steps, but no revision shown (no differences, no major bump, no change key) |
| 2026-11-25 | 1.3.1 | revise-needs-change, prompt naming the charter, after the in-place revision rule (headless, writes disallowed) | pass | Found CR-004 approved; revised ACME-PC-001 in place, 1.0.0 to 2.0.0 with `change: CR-004`; showed the differences as a diff; listed WBS, RACI, gate and risk follow-ups without editing them; wrote nothing |
