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
| 2026-11-25 | 1.3.0 | attribution-removed (headless, sonnet, writes disallowed) | pass | Kept the agreements; dropped who proposed, the personal reason and the vote; unanswered headings left as nothing to report |
| 2026-11-25 | 1.3.1 | prepare-workshop, record-from-notes, review-due, no-project-register (headless, writes disallowed) | prepare-workshop pass; record-from-notes partial; review-due pass; no-project-register pass | record-from-notes: the shown charter is `status: issued` but still carries an Open questions section with the code review question, then asks whether to issue or keep as draft; the question is listed for the user and the review date proposed, nothing written as an agreement. review-due: asks first whether the workshop is preparation or recording |
| 2026-11-25 | 1.3.1 | record-from-notes (re-run after fixes, headless, writes disallowed) | pass | Asked draft or issued before showing a document; the code review question listed for the user, not an agreement; review date proposed |
