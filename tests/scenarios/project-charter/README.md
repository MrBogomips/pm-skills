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
| revise-needs-change | issued | "Rimuovi il modulo pagamenti dallo scope" | Finds CR-004 approved; shows the differences; major version with `change: CR-004`; without an approved change it suggests `/pm-skills:change-request` |
| no-project-register | no project | "Write the project charter" | Suggests `/pm-skills:project-setup`; drafts in the session only if the user wants, asking for the facts; invents no configuration |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
