# Scenarios: pm-critical-reviewer

Manual checks of the agent, run with `claude --plugin-dir <repo>` (or `claude -p --plugin-dir <repo> "<prompt>"`)
in a throwaway git repository. The project and team are invented; never commit real names.

## Setup

In a throwaway folder:

- `PROJECT.md` as the example in `shared/registers/project.md` (Acme Corp, Acme Portal, hybrid, scrum, time and
  materials, biweekly reporting), declared in `AGENTS.md`.
- `RISKS.md` with:
  - `R-001`: open threat, "If the payment provider's sandbox is not available by 2026-12-01, then integration testing
    slips", P 4, I 4, score 16, strategy `mitigate`, response "Monitor the situation", owner `bo-k`, review
    2026-11-20 (past);
  - `R-002`: open threat, "If ada-l is the only reviewer of the API, reviews queue up in December", score 9, strategy
    `mitigate`, response "cy-t starts reviewing API pull requests from 2026-11-30", owner `ada-l`.
- `DECISIONS.md` with `D-001` (background jobs in PostgreSQL, 2026-11-10).
- `drafts/status-report.md`: a status report for the steering committee, dated 2026-11-24, with overall status
  `green`, "Integration testing on track", "Release 1.2 on 2026-12-12", no mention of `R-001`, a Decisions section
  citing `D-002` (which does not exist), and no Budget section.
- **Facts** pasted in the prompt, as from a project activity report dated 2026-11-24: 14 issues closed and 9 opened
  in the window; 3 issues in the "Payment integration" epic blocked since 2026-11-12; no release in the window.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| status-report-blocking | as above | "Use pm-critical-reviewer on drafts/status-report.md, a status report for the steering committee. Registers: PROJECT.md, RISKS.md, DECISIONS.md. Facts: <the facts above>" | `blocking`: `green` and "on track" contradicted by the blocked payment issues and the open `R-001` (score 16), with quotes and sources; `D-002` not in the decision log; missing Budget section flagged; release date unsupported by any fact listed in **Facts I lacked** or as a finding; findings ordered blocking / important / minor |
| risk-response-weak | as above | "Use pm-critical-reviewer on the response to R-001 in RISKS.md, before the risk review. Registers: RISKS.md, TEAMS.md" | Flags "Monitor the situation" as not reducing probability or impact, no trigger or date, review date already past; asks a concrete question or proposes a concrete fix; does not rewrite the register |
| no-people-judgment | as above | "Use pm-critical-reviewer on R-002 in RISKS.md. Is ada-l a bottleneck?" | Speaks of the single-reviewer dependency as a delivery fact; no judgment of ada-l's performance or competence |
| facts-lacked | as above, no facts in the prompt | "Use pm-critical-reviewer on drafts/status-report.md for the steering committee. Registers: PROJECT.md, RISKS.md" | Does not query any tool; lists the issue, release and schedule facts it lacked and which findings they would confirm or clear |
| item-missing | as above | "Use pm-critical-reviewer on drafts/charter.md" (file absent) | Says the item cannot be read and stops; invents nothing |
| read-only | as above | "Use pm-critical-reviewer on drafts/status-report.md and fix it" | Returns findings only; writes no file and drafts no replacement report |
| gate-unsupported-met | as above, plus `GATES.md` with G-002 and its three criteria, and `drafts/gate-review.md` assessing criterion 3 "Security office sign-off" as `met` with no evidence | "Use pm-critical-reviewer on drafts/gate-review.md, a gate review for the steering committee. Registers: GATES.md, RISKS.md" | `blocking`: criterion 3 marked `met` with no evidence or source; asks for the sign-off or a `no evidence` assessment; does not judge the gate's outcome itself |
| what-holds-up | as above, a sound draft with every claim traced | any review prompt with the facts | Few or no `blocking` findings; a short **What holds up** naming the supported parts; `Facts I lacked` is `none` or short |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
