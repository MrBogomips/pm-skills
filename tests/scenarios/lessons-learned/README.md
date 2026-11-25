# Scenarios: lessons-learned

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **closing**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md`, with `GATES.md`, `DECISIONS.md`, `CHANGES.md`, `RISKS.md`, `TEAMS.md` from `tests/fixtures/`; three
  retrospectives in `retrospective/`, two of which list "flaky end-to-end tests" under Change; two gate reviews.
- **no sources**: `PROJECT.md` only, with no other register and no documents.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| at-closing-gate | closing | "Write the lessons learned for the project" | Context with gate outcomes (G-002 held once on criterion 3); the recurring flaky tests theme with its source; recommendations addressed to next project or organization; follow-up only with owner and date |
| mid-project-phase | closing | "Lezioni apprese della fase di discovery" | Scoped to G-001 with `gate: G-001` and the period; talks in Italian, writes in the `Deliverable language` |
| person-remark-rephrased | closing | "Add that bo-k kept breaking the build" | Rephrases as a condition of the way of working (build checks before merge) or leaves it out and says why; no name |
| no-sources | no sources | "Lessons learned" | Names the sources it could not read; asks for notes instead of inventing points |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.3.0 | person-remark-rephrased (headless, sonnet, writes disallowed) | pass | No name; rephrased as a pre-merge check; marked the point unsourced; follow-up without a date held as open |
| 2026-11-25 | 1.3.1 | at-closing-gate, mid-project-phase, no-sources (headless, writes disallowed) | at-closing-gate pass; mid-project-phase partial; no-sources pass | mid-project-phase: scoped to G-001 with the gate key and the period, but the document is in English (the fixture's Deliverable language) while the chat was in Italian; the Expected 'in Italian' conflicts with the fixture. at-closing-gate: follow-up owners and dates proposed by the skill, marked as to confirm |
| 2026-11-25 | 1.3.1 | mid-project-phase (re-run after fixes, headless, writes disallowed) | pass | Chat in Italian; document in English per the Deliverable language; scoped to G-001 with the gate key and period |
