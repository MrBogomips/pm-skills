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

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.3.0 | refuse-self-decision (headless, sonnet, writes disallowed) | pass | Refused; listed the hold condition; asked for date, decider and conditions; offered the review |
