# Scenarios: communication-plan

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **registers**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md` (biweekly reporting, Scrum, two-week sprints), with `STAKEHOLDERS.md`, `RACI.md`, `GATES.md` and
  `TOOLS.md` from `tests/fixtures/`.
- **no stakeholders**: **registers** without the `Stakeholder register` line and without `STAKEHOLDERS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| from-registers | registers | "Draft the communication plan" | Audiences by role with S- IDs; status report biweekly with Produced by `status-report`; Security office consulted on RA-001 and RA-002 among the audiences; meetings and escalation path; shown before writing |
| stakeholder-without-communication | registers | "Check the communication plan" | Flags each active stakeholder below its desired engagement with no communication; suggests `/pm-skills:stakeholder-register` where the approach needs changing; never edits STAKEHOLDERS.md |
| no-contacts | registers | "Add the sponsor's email address to the plan" | Refuses: channels name the means, not addresses |
| no-stakeholder-register | no stakeholders | "Piano di comunicazione" | Says the stakeholder register is not declared; asks for the audiences; answers in Italian |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.3.0 | no-contacts (headless, sonnet, writes disallowed) | partial | Refused; but suggested the stakeholder register for contacts: Never rule tightened |
| 2026-11-25 | 1.3.1 | from-registers, stakeholder-without-communication, no-contacts (re-run), no-stakeholder-register (headless, writes disallowed) | from-registers pass; stakeholder-without-communication pass; no-contacts pass; no-stakeholder-register partial | no-contacts: refused and suggested no register for contacts (the earlier gap is closed); run with an issued plan present. stakeholder-without-communication: run with an issued plan covering only the sponsor; the proposed fixes name a person slug as owner of a communication. no-stakeholder-register: Italian, said the register is not declared, but offered two routes instead of asking for the audiences |
| 2026-11-25 | 1.3.1 | no-stakeholder-register (re-run after fixes, headless, writes disallowed) | pass | Italian; said the register is missing; proposed audiences from RACI and gates as roles and asked to confirm and complete them; suggested stakeholder-register for the lasting fix |
