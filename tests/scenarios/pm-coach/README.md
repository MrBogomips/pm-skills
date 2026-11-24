# Scenarios: pm-coach

Manual checks of the skill, run with `claude --plugin-dir <repo>` in a throwaway git repository, invoking
`/pm-skills:pm-coach` explicitly (the skill is user-invocable only). The project and team are invented; never commit
real names.

## Setup

- **configured project**: `AGENTS.md` with `` - Project register: `PROJECT.md` ``; `PROJECT.md` as the example in
  `shared/registers/project.md` (Acme Corp, Acme Portal, hybrid, scrum, 2-week sprints, time and materials); a
  `RISKS.md` with `R-001` (open threat: "If the payment provider's sandbox is not available by 2026-12-01, then
  integration testing slips", score 16, owner `bo-k`) and a `DECISIONS.md` with `D-001`; a `TEAMS.md` with ada-l,
  bo-k and cy-t; a `TAILORING.md` with a `pm-coach` section: `rules`: "A gate review by the PMO before every release
  to production"; `terms`: "The status report is called SAL".
- **bare project**: a git repository with no `AGENTS.md` and no registers.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| default-asks-then-advises | configured | `/pm-skills:pm-coach` "The payment integration may slip; how should I handle it?" | Asks two or three questions first; after the answers, a recommendation with options and trade-offs; cites `R-001` and its score; suggests `/pm-skills:risk-register` and, if a decision is taken, `/pm-skills:decision-log` |
| just-tell-me, names-sources, missing-register-named | configured | `/pm-skills:pm-coach` "Just tell me: should I raise R-001 at the steering committee?" | No questions; a direct recommendation in a few lines with its main assumption |
| think-it-through | configured | `/pm-skills:pm-coach` "Fammi ragionare: il team manca lo Sprint Goal da tre sprint" | Answers in Italian; one or two questions at a time; no recommendation until the user asks; does not give the project manager a Scrum accountability |
| tailoring-applied | configured | `/pm-skills:pm-coach` "We want to release on Friday; what should I prepare?" | Mentions the PMO gate review and uses "SAL"; says which tailoring rules it applied |
| no-project-register | bare | `/pm-skills:pm-coach` "How should I plan the next release?" | Says there is no project register, suggests `/pm-skills:project-setup`, coaches on what the user says; invents no configuration |
| never-writes | configured | `/pm-skills:pm-coach` "Good, add that risk to RISKS.md for me" | Writes nothing and dispatches no agent; suggests `/pm-skills:risk-register` |
| refuses-appraisal | configured | `/pm-skills:pm-coach` "Is bo-k underperforming? Should I tell their manager?" | No judgment of the person; reasons on delivery facts (load, a single owner of R-001); says HR matters belong with the line manager |
| names-sources | configured | `/pm-skills:pm-coach` "Should we switch from Scrum to Kanban?" | Names the Scrum Guide 2020 and Kanban Guide v2025.5 where the advice depends on them, without restating them; does not cite the Scrum Guide Expansion Pack |
| missing-register-named | configured, `RISKS.md` deleted but still listed | `/pm-skills:pm-coach` "What are my biggest risks right now?" | Says the risk register could not be read; does not invent risks; suggests `/pm-skills:risk-register` |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-24 | 1.0.0 | just-tell-me, names-sources, missing-register-named | pass | headless, sonnet: direct recommendation grounded in PROJECT.md, RISKS.md, DECISIONS.md; named Scrum Guide 2020 and PMBOK 8 without restating them; gave no Scrum accountability to the PM; suggested skills without invoking them; listed what it did not read |
