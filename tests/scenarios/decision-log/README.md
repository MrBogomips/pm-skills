# Scenarios: decision-log

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **no log**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md` with the `Decision log` line removed; no `DECISIONS.md`.
- **declared**: `AGENTS.md` as above; `tests/fixtures/PROJECT.md`, `DECISIONS.md`, `TEAMS.md` and `TAILORING.md`
  copied at the root.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| setup-proposes-log-and-line | no log | "Set up the decision log" | Proposes `DECISIONS.md` with the title only and the line `- Decision log: \`DECISIONS.md\`` under Registers; writes after the user agrees; both files validate |
| record-asks-only-missing | declared | "Record a decision: we use OpenAPI 3.1 for the public API" | Asks for who decided, when and the context (not for keys already given); proposes D-003 with Status accepted; shows before writing; the file validates |
| record-refuses-discussion | declared | "Registra una decisione: in riunione ci siamo orientati verso GraphQL, ne riparliamo la prossima settimana" | Says no decision was taken and records nothing; offers to record it when decided; answers in Italian |
| we-is-not-decided-by | declared | "Record that we decided to freeze features on 2026-12-01" | Asks who decided ("we" is not enough) |
| supersede-links-both | declared | "The steering committee decided today to drop the broker and use the cloud provider's queue service" | Detects that D-002 is in force on the same subject; proposes D-003 with `Supersedes: D-002` and D-002 changed only to `superseded` with `Superseded by: D-003`, in one write; the file validates |
| revoke-without-rewrite | declared | "Revoke D-002" | Changes only D-002's Status to `revoked`; offers to record the withdrawal as a new decision without a `Supersedes` link; never edits D-002's other entries |
| find-follows-chain | declared | "Cosa avevamo deciso sui job in background?" | Answers with D-002 in force, who decided and why, and mentions D-001 it replaced; quotes the log |
| find-nothing | declared | "What did we decide about the mobile app?" | Says the log holds no such decision; does not guess |
| proposes-risk | declared | "Record a decision: the tech lead decided today to depend on the provider's beta SDK for payments, because the stable one lacks refunds" | Records after confirmation and proposes a candidate risk (beta SDK may change), suggesting `/pm-skills:risk-register`; does not touch `RISKS.md` |
| no-project-register | no project | "Record a decision" | Suggests `/pm-skills:project-setup`; goes on only on a path the user names; invents no configuration |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-24 | 1.0.0 | find-follows-chain, proposes-risk | pass | headless, sonnet: answered with D-002 in force, followed the supersession to D-001, quoted the log, suggested a risk without writing |
