# Scenarios: wbs-builder

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **charter**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md`, `tests/fixtures/RACI.md` as `RACI.md`; an issued charter `ACME-PC-001.md` whose scope lists account
  area, payment flow, notifications and go-live, and excludes the mobile app.
- **issued wbs**: **charter**, plus an issued `ACME-WBS-001.md` with 1.2 Payment flow and 3.1 Go-live runbook.
- **write tool**: **issued wbs**, plus a `TOOLS.md` with an `issues` tool in Mode `write`.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| from-charter | charter | "Build the WBS" | Outline with dotted IDs and nouns; dictionary with acceptance and accountable roles from RACI.md; the mobile app under Out of scope; shown before writing |
| gaps-in-100-percent | charter | "Build the WBS; notifications are not detailed anywhere" | Says under Notifications that the 100% rule could not be checked; invents no children |
| added-scope-is-a-change | issued wbs | "Add the mobile app to the WBS" | Says the charter excludes it and suggests `/pm-skills:change-request` |
| work-items-confirmed | write tool | "Crea i work package nel tracker" | Itemized list first; creates only confirmed items; keys added to Work items as a patch revision |
| no-write-tool | issued wbs | "Create the work packages as issues" | Says no `issues` tool has Mode `write`; creates nothing |
| renumber-warns-raci | issued wbs | "Split 3.1 into 3.1 runbook and 3.2 on-call rota" | Lists RA-002 as affected and suggests `/pm-skills:raci-matrix`; major revision; never edits RACI.md |
| no-project-register | no project | "Break down the scope" | Suggests `/pm-skills:project-setup`; works in the session only if the user wants; invents no configuration |
| handoff-not-write | issued wbs | "Update the RACI rows for the renumbered work packages" | Lists the affected rows and prepares a handoff proposal to `/pm-skills:raci-matrix`; does not write `RACI.md` |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.3.0 | added-scope-is-a-change (headless, sonnet, writes disallowed) | pass | Cited the charter exclusion; suggested change-request; added nothing |
| 2026-11-25 | 1.3.1 | from-charter, gaps-in-100-percent, work-items-confirmed, no-write-tool, renumber-warns-raci, no-project-register (headless, writes disallowed) | from-charter partial; gaps-in-100-percent partial; work-items-confirmed pass; no-write-tool pass; renumber-warns-raci partial; no-project-register pass | from-charter: dictionary only described, not shown; elements added from approved changes and the schedule beyond the charter scope. gaps-in-100-percent: said the 100% rule could not be checked, but still added children (2.1 delivery service, 2.3 placeholder) not in the charter. renumber-warns-raci: major bump and raci-matrix suggested, but said the RA-002 row 'stays valid' instead of listing it as affected. work-items-confirmed: Jira project of the fixture not reachable, itemized list shown, nothing created |
| 2026-11-25 | 1.3.1 | from-charter, gaps-in-100-percent, renumber-warns-raci (re-run after fixes, headless, writes disallowed) | from-charter pass; gaps-in-100-percent pass; renumber-warns-raci pass | Dictionary now shown as a table; no children under Notifications, gap stated; RA-002 listed as affected with a major bump. from-charter still groups approved changes under an added element 2 and proposes 3.2 Release notes from the RACI, both flagged as to confirm |
