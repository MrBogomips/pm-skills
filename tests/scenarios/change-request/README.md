# Scenarios: change-request

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **no log**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md`; no `Change log` line and no `CHANGES.md`.
- **declared**: `AGENTS.md` as above; `tests/fixtures/PROJECT.md` with the line `- Change log: \`CHANGES.md\`` added
  under Registers; `RISKS.md`, `DECISIONS.md`, `TEAMS.md` and `TAILORING.md` from `tests/fixtures/` at the root; a
  `CHANGES.md` with CR-001 `approved` (Decided by steering committee, Decided on 2026-10-02), CR-002 `implemented`
  and CR-003 `proposed` (export of invoices to CSV, Requested by Client finance); no `TOOLS.md`.
- **approval rule**: **declared**, plus in `TAILORING.md` a `## change-request` section with `### rules`: "A change
  over 5 person-days or 5,000 EUR needs the steering committee; below that, the project manager decides."
- **with tools**: **approval rule**, plus a `TOOLS.md` with an issues tracker the session can read and a `file:`
  schedule and costs spreadsheet with rates per role.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| setup-proposes-log-and-line | no log | "Set up the change log" | Proposes `CHANGES.md` with the title and the line `- Change log: \`CHANGES.md\`` under Registers; writes nothing before the user agrees; both files validate |
| raise-next-id | declared | "Raise a change request: the client wants SSO for partners before the December release" | Proposes CR-004, Status proposed, Raised today; asks for Requested by and Reason if missing; shows the section before writing; the file validates |
| duplicate-pointed-out | declared | "Raise a change request: export invoices to CSV" | Points to CR-003 as the same request; raises nothing new unless the user insists it differs |
| no-approver-rule | declared | "Assess CR-003" | Says the project names no approver in its tailoring and asks who decides; invents no threshold |
| assess-from-facts | with tools | "Assess CR-003, the team estimates 6 to 9 person-days" | Four impacts each tied to a source (issues, schedule, costs, risk register); effort from the user's range, cost from rates per role; names the steering committee as approver under the rule (over 5 person-days); says which sources were unavailable |
| reviewer-before-assessed | with tools | "Assess CR-003" | Dispatches `pm-critical-reviewer` with the draft, approvers as audience, register paths and tool facts before marking it assessed; findings shown as proposals or open points |
| fable-on-three-domains | with tools | "Assess CR-004" where schedule, cost and risk impacts are not none | Announces the escalation to `fable` and why before dispatching; with fewer than three impacts and no steering or client audience, no escalation |
| decision-needs-approver | approval rule | "CR-003 approved by the project manager" after an assessment over 5 person-days | Says the rule requires the steering committee and does not mark it approved |
| decision-recorded-and-logged | approval rule | "CR-003 approved by the steering committee on 2026-11-27" | Status approved with Decided by and Decided on; offers a decision-log handoff proposal (Source the change log), never writes `DECISIONS.md` itself; after the keeper reports D-003 adds `Decision: D-003`; `CHANGES.md` validates |
| risk-proposed | approval rule | "CR-003 approved ..." where the impact adds a dependency | Proposes a new risk as cause, event and effect in a handoff proposal to `/pm-skills:risk-register` (no ID); asks for Strategy, Owner and Review; never writes `RISKS.md` |
| handoff-from-minutes | declared | A handoff proposal from meeting-minutes: add a change request "move go-live to January", requested by the sponsor | Offers (a) record as proposed, (b) assess now, (c) reject at once, (d) not record; with (d) nothing is written; with (a) CR-004 proposed and its ID reported back |
| reject-at-once | declared | "Record CR-004 and reject it now, the steering committee decided, no assessment" | Asks who had the authority; writes `rejected`, `Recommendation: not assessed`, Decided by and Decided on, no impacts; `CHANGES.md` validates; offers a decision-log handoff |
| reject-at-once-authority | declared | "Reject CR-003 right away" without saying who decides | Asks who has the authority; the project manager only if they hold it; writes nothing until answered |
| implemented-only-if-approved | declared | "Mark CR-003 implemented" | Refuses: CR-003 is not approved; suggests assessing and deciding first |
| no-rewrite-after-decision | declared | "Change the description of CR-001" | Refuses to change the content of a decided request; allows a correction of form only; suggests a new request |
| people-rule | declared | "Raise a change request from Bo, the client's lazy PM, at bo@example.com" | Records the requester as a role; leaves out the judgment and the contact and says why |
| no-project-register | no project | "Raise a change request" | Suggests `/pm-skills:project-setup`; goes on only on a path the user names; invents no configuration |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.1.0 | raise-next-id (headless, sonnet, writes disallowed) | pass | CR-004 proposed, Raised 2026-11-25, asked Requested by and Reason; shown before writing; sandbox CHANGES.md was incomplete, so it also reported validation errors |
