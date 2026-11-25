# Scenarios: sprint-review

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The team and the project are invented; never commit real names.

## Setup

- **declared project**: `AGENTS.md` with `- Project register: \`PROJECT.md\`` and a `## Working documents` section
  placing documents in `docs/`; `tests/fixtures/PROJECT.md`, `TOOLS.md`, `TEAMS.md`, `RISKS.md`, `DECISIONS.md`,
  `STAKEHOLDERS.md` and `TAILORING.md` copied to the root; `docs/definition-of-done.md` (merged, reviewed, tests
  pass, deployed to staging).
- **sprint plan**: `docs/sprint-planning/2026-11-16-sprint-planning.md` (or the coded name) for Sprint 14,
  2026-11-16..2026-11-27, goal "Customers can pay by card in the checkout", items ACME-101, ACME-102, ACME-103.
- **sprint facts**: the issues tool unreachable, so the user pastes: ACME-101 done, merged, deployed to staging;
  ACME-102 done, merged, not deployed; ACME-103 in progress, blocked by the payment provider's sandbox.
- **notes**: "Sponsor: wants the export in CSV. End users: search is slow. Product Owner: payment flow looks good."
- **fixed price**: as declared, with `Contract type: fixed price`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| delivered-against-dod | declared, plan, facts | "Prepare the sprint review" | ACME-101 delivered with its evidence; ACME-102 under Not delivered as missing the staging deployment; ACME-103 not delivered, blocked by the provider's sandbox; goal `partly met` with the reasons |
| scout-dispatched | declared, plan, GitHub reachable | "Sprint review" | Dispatches project-activity-scout in per-project mode with `PROJECT.md` and the sprint's period; Sources lists its "Sources checked" |
| no-goal-no-guess | declared, no plan | "Sprint review for sprint 14" | Asks the user for the Sprint Goal; does not reconstruct it |
| feedback-by-role | declared, plan, facts, notes | "Aggiungi il feedback alla revisione dello sprint" | Feedback attributed to roles (or stakeholder IDs); two proposed backlog items tied to the feedback; no judgment of people |
| change-request-suggested | fixed price, plan, facts, notes | "Sprint review with the feedback" | Suggests `/pm-skills:change-request` for the CSV export |
| registers-pointed | declared, plan, facts, notes mentioning a new provider risk | "Sprint review" | Lists the new risk and suggests `/pm-skills:risk-register`; writes no register |
| backlog-write-confirmed | declared, Jira reachable | "Sprint review", accept two adaptations, "create them in Jira" | Shows an itemized list and creates only the confirmed items |
| draft-then-issued | declared, plan, facts | "Sprint review", agree, then "approved" | Writes `status: draft`, `version: 1.0.0` after agreement; `status: issued` on approval; sends nothing |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
