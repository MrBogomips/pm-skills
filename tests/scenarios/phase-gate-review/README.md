# Scenarios: phase-gate-review

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **no register**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md` without the `Gate register` line; `RISKS.md`, `DECISIONS.md`, `SCHEDULE.md`, `CHANGES.md` from
  `tests/fixtures/`; a `project-charter/` document listing the phases Discovery, Build, Go-live.
- **declared**: **no register**, plus the `Gate register` line and `tests/fixtures/GATES.md` as `GATES.md` (G-002
  open after a hold on criterion 3).
- **passed with conditions**: **declared**, with G-002 `passed` after `go with conditions` "Pen test fixes by
  2026-12-11 (criterion 3)".
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| define-gates | no register | "Set up the phase gates" | Proposes `GATES.md` and the Registers line; gates from the charter's phases with criteria the user confirms; writes after agreement; both files validate |
| review-with-missing-evidence | declared | "Prepare the gate review for G-002" | Every criterion assessed with its source; criterion 3 `no evidence` or `not met`, never `met` without a fact; the hold's condition listed with its state; Decision "pending" |
| critic-escalation-steering | declared | "Prepare G-002 for the steering committee" | Tells the user the review goes to `pm-critical-reviewer` escalated to `fable` and why; offers to decline; shows the findings |
| record-go-with-conditions | declared | "The steering committee decided go with conditions today: pen test fixes by 11 December" | Appends the outcome with the condition and date, sets G-002 `passed`, fills the Decision as a patch revision; shows both before writing; register validates |
| follow-up-conditions | passed with conditions | "Review G-002 again" | Lists the pen test condition with its state from the facts or "to confirm"; proposes a `go` row only if the user reports that decision |
| refuse-self-decision | declared | "Just mark G-002 as go" | Refuses to record an outcome nobody decided; says who decides and offers to prepare the review |
| frozen-criteria | passed with conditions | "Change criterion 2 of G-002" | Explains the criteria of a decided gate are frozen; proposes a new gate |
| closing-gate-suggests-lessons | declared, a closing gate G-003 | "The sponsor approved closing the project today" | Records the outcome, then suggests `/pm-skills:lessons-learned` |
| no-project-register | no project | "Are we ready for go-live?" | Suggests `/pm-skills:project-setup`; goes on only on a path the user names; invents no configuration |
| handoff-accepted | declared | A handoff proposal from project-charter: add gate G-003 with two criteria | Checks the proposal against the format, computes the ID, shows, writes on agreement, validates and reports the ID |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.3.0 | refuse-self-decision (headless, sonnet, writes disallowed) | pass | Refused; listed the hold condition; asked for date, decider and conditions; offered the review |
| 2026-11-25 | 1.3.1 | define-gates, review-with-missing-evidence, critic-escalation-steering, record-go-with-conditions, follow-up-conditions, frozen-criteria, closing-gate-suggests-lessons, no-project-register (headless, writes disallowed) | define-gates pass; review-with-missing-evidence pass; critic-escalation-steering partial; record-go-with-conditions pass; follow-up-conditions pass; frozen-criteria pass; closing-gate-suggests-lessons pass; no-project-register pass | critic-escalation-steering: findings shown, but the review had already been dispatched on the escalated model when the user was told and offered the decline (headless run; the same happened in review-with-missing-evidence and follow-up-conditions). closing-gate-suggests-lessons: first run with the preceding gate still on hold asked questions instead of recording; with the preceding gate passed and the decision stated it showed the outcome row, the status change and suggested lessons-learned. record-go-with-conditions: no review document in the fixture, so no Decision patch to show |
| 2026-11-25 | 1.3.1 | critic-escalation-steering (re-run after fixes, headless, writes disallowed) | pass | Told the user about the escalated review and asked whether to decline before dispatching it; the review itself was therefore not run in this turn, so the findings were not shown |
| 2026-11-26 | 1.6.0 | handoff-accepted | pass | headless, sonnet, declared: skill loaded through the Skill tool with the proposal as args; computed G-003, showed gate and criteria, flagged the past planned date and the order against G-002, asked who decides; validated GATES.md; nothing written |
