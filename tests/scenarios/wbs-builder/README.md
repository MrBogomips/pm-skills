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

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
