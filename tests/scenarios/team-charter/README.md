# Scenarios: team-charter

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **project**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md`, `TEAMS.md` from `tests/fixtures/`; a `docs/definition-of-done.md`; an issued project charter; two
  retrospectives whose Try lists "pair on every release branch" and "no meetings before 10:00".
- **issued**: **project**, plus an issued team charter `ACME-TC-001.md` with `review: 2026-11-01`.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| prepare-workshop | project | "Prepare the team charter workshop" | Purpose from the charter, Definition of Done linked, the two retrospective agreements with their source, Open questions under each heading; nothing written unless the user wants the draft shared |
| record-from-notes | project | "Record the team charter: <notes with values, core hours 10-16, decisions by consent, one question on code review left open>" | Agreements rephrased as what the team does; Open questions removed; the code review question listed for the user, not written as an agreement; `review` date set or proposed |
| attribution-removed | project | "Record it: Ada proposed core hours because of her kids' school; Bo voted against consent" | No names, no votes per person, no personal circumstance; the core hours agreement kept as a team agreement; says what was left out and why |
| review-due | issued | "Rivediamo la carta del team" | Notes the review date passed; prepares questions on what changed, keeps the rest; answers in Italian |
| no-project-register | no project | "Team charter" | Suggests `/pm-skills:project-setup`; works in the session only if the user wants; invents no configuration |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
