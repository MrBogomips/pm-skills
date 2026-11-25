# Scenarios: retrospective

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The team and the project are invented; never commit real names.

## Setup

- **declared project**: `AGENTS.md` with `- Project register: \`PROJECT.md\`` and a `## Working documents` section
  placing documents in `docs/`; `tests/fixtures/PROJECT.md`, `TOOLS.md`, `TEAMS.md` and `TAILORING.md` copied to the
  root.
- **previous retrospective**: `docs/retrospective/2026-11-13-retrospective.md` (or the coded name), `status:
  issued`, with Actions: 1 "Add a staging smoke test to the release pipeline", `bo-k`, 2026-11-25; 2 "Limit work in
  progress to 4 items", team, 2026-11-20.
- **sprint facts**: the tools unreachable, so the user pastes: 9 of 11 planned items done; 2 items bounced back from
  review twice; one failed release build on 2026-11-24; WIP above 4 on three days.
- **notes**: "Keep: pairing on reviews. Change: ada-l never answers in chat, very annoying (said cy-t). Try: a
  review slot every morning. Votes: bo-k 3, cy-t 2. Action: cy-t to set up the review slot by 2026-12-04. Someone
  should fix the flaky test."
- **kanban**: as declared, with `Agile framework: kanban`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| prepare-facts | declared, previous, facts | "Prepare the retro" | Facts by team from what was given; both previous actions listed with state, "to confirm with the team" where the facts do not show it; Keep, Change, Try and Actions empty; nothing written unless asked |
| record-people-rule | declared, previous, notes | "Registra la retrospettiva" | No "said cy-t", no votes per person; the chat point rephrased as a way-of-working point (response times in chat) or left out with the reason told to the user |
| action-owner-date | declared, previous, notes | "Record the retrospective" | The review-slot action written with `cy-t` and 2026-12-04; the flaky-test action not written, asked about or listed as open for the team |
| previous-followed-up | declared, previous, notes | "Record the retrospective" | Each previous action has a state; an unfinished one is carried into Actions or marked `dropped` with the team's reason |
| draft-completed | declared, a draft written at preparation | "Record the retrospective" | Completes the same file, raises the version as minor, `status: issued` on approval |
| actions-as-items | declared, Jira reachable | "Record the retrospective, then create the actions in Jira" | Itemized list, creates only confirmed items, adds their keys as a patch revision |
| kanban-period | kanban, previous | "Prepara la retro" | Period from the previous retrospective to today; no sprint in the frontmatter |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.1.0 | record-people-rule + action-owner-date (notes, tools unreachable) (headless, sonnet, writes disallowed) | pass | No attribution or per-person votes; chat point rephrased; review-slot action with cy-t and 2026-12-04; flaky test asked about |
