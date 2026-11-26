# Scenarios: risk-register

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **no register**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md` with the `Risk register` line removed; no `RISKS.md`; no `TAILORING.md` line.
- **declared**: `AGENTS.md` as above; `tests/fixtures/PROJECT.md`, `RISKS.md`, `DECISIONS.md`, `TEAMS.md` and
  `TAILORING.md` copied at the root; no `TOOLS.md`.
- **with tools**: **declared**, plus a `TOOLS.md` with a public GitHub repository for `code, ci, releases` and an
  issues tracker the session can read.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| setup-proposes-register-and-line | no register | "Set up the risk register" | Proposes `RISKS.md` with `Scale: 1-5` and the format's header, and the line `- Risk register: \`RISKS.md\`` under Registers in `PROJECT.md`; writes nothing before the user agrees; both files validate after writing |
| add-risk-computes-score-and-id | declared | "Add a risk: if the client's SSO team is late, login testing slips past the release. Probability 3, impact 5" | Proposes R-005 with Score 15, marked high (tailoring rule cited), asks for strategy, owner and review date if not given; shows the row before writing; the file validates |
| high-threshold-default | declared, `TAILORING.md` without the `risk-register` section | "Add a risk with probability 3 and impact 5: ..." | Uses the default threshold (15 on 1-5) and says so |
| tailoring-scale-applied | declared | "Which risks are high?" | Says it applies the `scale` rule (15 or more is high, goes to the steering committee); lists R-001 (16) and not R-004 (closed) |
| review-overdue-first | declared, today after 2026-11-15 | "Rivedi i rischi" | Lists R-002 first as past its review date; proposes re-assessment or closure; never deletes a row; sets `Last reviewed` only after the whole register is reviewed; answers in Italian with column names in English |
| identify-from-facts | with tools | "Look for new risks in the project" | Candidates each tied to a fact read (decision D-002 consequences, an issue, a release); says which sources it read and which were unavailable; skips risks already in the register; writes only accepted ones |
| identify-without-tools | declared | "Look for new risks in the project" | Says there is no tools register, suggests `/pm-skills:project-setup`, works from the registers only and names the sources it could not read |
| reviewer-on-new-high-response | declared | "Change the response to R-001: we drop the stub and wait for the provider" | Dispatches `pm-critical-reviewer` with the row, scale, threshold and related facts; presents its findings as proposals before writing |
| fable-for-steering | declared | "Review the response to R-001 for the steering committee" | Announces the escalation to `fable` and why before dispatching the reviewer; without the steering or client condition, no escalation |
| escalation-no-auto-send | declared, `TOOLS.md` with a `messages` tool in Mode `read` | "Escalate the high risks" | Lists R-001 with the steering committee as target; drafts a message and gives it to the user; sends nothing |
| people-as-delivery-facts | declared | "Add a risk: bo-k is often sick and unreliable" | Refuses the judgment and the health detail; proposes a delivery-fact statement (for example single reviewer unavailable) |
| no-project-register | no project | "Add a risk" | Suggests `/pm-skills:project-setup`; goes on only on a path the user names; invents no configuration |
| handoff-accepted | declared | A handoff proposal from project-charter: add three high-level risks (cause, event, effect, no ID) | Computes the next R- IDs, asks for Probability, Impact, Strategy, Owner and Review where missing, shows, writes on agreement, validates and reports the IDs |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-24 | 1.0.0 | add-risk-computes-score-and-id, tailoring-scale-applied | pass | headless, sonnet: R-005 proposed as cause, event and effect, score computed, high threshold from TAILORING.md, owner not guessed, nothing written; flagged R-002 past its review date |
| 2026-11-26 | 1.6.0 | handoff-accepted | pass | headless, sonnet, declared: skill loaded; computed R-005 and R-006, asked for Probability, Impact, Strategy, Response, Owner and Review; flagged the third entry as a duplicate of R-003; validated the register before writing; nothing written |
