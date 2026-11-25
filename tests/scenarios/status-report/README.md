# Scenarios: status-report

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The team and the project are invented; never commit real names.

## Setup

- **declared project**: `AGENTS.md` with `- Project register: \`PROJECT.md\`` and a `## Working documents` section
  placing documents in `docs/`; `tests/fixtures/PROJECT.md` (biweekly cadence, coded naming, `status-report=SAL`),
  `TOOLS.md`, `TEAMS.md`, `RISKS.md`, `DECISIONS.md` and `TAILORING.md` copied to the root; GitHub pointing to a
  public repository as in the project-activity-scout scenarios.
- **previous report**: `docs/ACME-SAL-001.md` with `period: 2026-10-28..2026-11-10`, `status: issued`.
- **no cadence**: as declared, with `Reporting cadence` removed from `PROJECT.md` and no previous report.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| period-from-previous | declared, previous report | "Status report" | Proposes period 2026-11-11..2026-11-24; dispatches project-activity-scout in per-project mode with `PROJECT.md` and a 14-day window |
| applies-tailoring | declared, previous report | "Status report for the team" | Says it applies the `format` and `terms` rules: title uses "SAL", a "Client actions" section after "Risks and issues"; name `docs/ACME-SAL-002.md` |
| all-headings-kept | declared, no costs data reachable | "Status report for the team" | Every heading present; Budget says not tracked or not readable; Sources names what could not be read |
| colors-with-reasons | declared, R-001 open with score 16 | "Status report" | Every color has a reason from the facts; R-001 appears among top open risks with its ID |
| review-for-client | declared, previous report | "Prepara il SAL per il comitato del cliente" | Announces the review by pm-critical-reviewer escalated to fable and why; on decline, runs it on the agent's own model; gives the reviewer the draft and the facts; shows the open points with the draft |
| no-review-for-team | declared | "Status report for the team only" | No critical review dispatched |
| draft-then-issued | declared | "Status report", agree to write, then "approved" | Writes with `status: draft`, `version: 1.0.0` only after agreement; sets `status: issued` on approval; suggests `/pm-skills:publish-deliverable`; sends nothing |
| asks-period-without-cadence | no cadence | "Report di avanzamento" | Proposes a period and asks before gathering facts |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-24 | 1.0.0 | applies-tailoring, all-headings-kept, colors-with-reasons, no-review-for-team | pass | headless, sonnet: `ACME-SAL-001.md` with the SAL term and the Client actions section from TAILORING.md; amber justified by R-001; empty sections say why; Sources lists what could not be read; no review for a team audience; nothing written |
| 2026-11-25 | 1.5.0 | Italian request ("Prepara il SAL per il comitato") | pass | headless, sonnet, declared: the skill loaded from the Italian request with an English-only description; the project's `terms` ("SAL") and `Deliverable language: English` won over the glossary, as designed: the draft was in English, named `ACME-SAL-001.md`, and the skill offered Italian |
