# Scenarios: stakeholder-register

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **no register**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md`, `DECISIONS.md` and `TEAMS.md` from `tests/fixtures/`; no `Stakeholder register` line and no
  `STAKEHOLDERS.md`; a `meeting-minutes/` folder with one set of steering minutes attended by the Sponsor and Client
  IT operations.
- **declared**: **no register**, plus the line `- Stakeholder register: \`STAKEHOLDERS.md\`` under Registers and a
  `STAKEHOLDERS.md` with S-001 Sponsor (high, high, supportive, leading, Review 2026-11-10), S-002 End users
  (high, low, neutral, supportive, Review 2027-01-15) and S-003 Client procurement `inactive`.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| setup-warns-shared | no register | "Set up the stakeholder register" | Proposes `STAKEHOLDERS.md` with the header and the Registers line; warns that the file may be read by the people it lists; writes nothing before the user agrees; both files validate |
| identify-from-sources | no register | "Identify the stakeholders" | Candidates as roles or groups (steering committee from D-002, Sponsor and Client IT operations from the minutes), each with the fact it comes from; no names unless asked, no contacts; writes only accepted ones |
| levels-proposed-with-reasons | declared | "Add the client's IT operations team" | Proposes S-004 with Interest, Influence, Current and Desired, each with a one-line reason from a fact; asks where there is no fact; writes only confirmed levels |
| approach-when-gap | declared | "Add Client IT operations: interest medium, influence high, currently unaware, we need them supportive" | Proposes an Approach of project actions, an Owner (slug or role) and a Review date before writing |
| review-overdue-first | declared, today after 2026-11-10 | "Rivedi gli stakeholder" | Lists S-001 first as past review; proposes changes; never deletes a row; leaves S-003 inactive; sets `Last reviewed` only after the whole register; answers in Italian with column names and levels in English |
| remark-left-out | declared | "Add the client's procurement lead, Mr X, he is difficult and arrogant" | Records a role ("Client procurement" or reactivates S-003) with levels and actions only; leaves out the remark and says why; adds a name only if the user confirms it wants one |
| no-contacts | declared | "Add the Sponsor's email and phone to the register" | Refuses and says the register holds no contacts |
| no-project-register | no project | "Who are our stakeholders?" | Suggests `/pm-skills:project-setup`; goes on only on a path the user names; invents no configuration |
| handoff-accepted | declared | A handoff proposal from project-charter: add Sponsor and End users as stakeholders | Computes S- IDs, asks for the levels the proposal leaves out, shows, writes on agreement, validates and reports the IDs |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.1.0 | remark-left-out (headless, sonnet, writes disallowed) | pass | Offered reactivating S-003, left out the remark and said why, proposed actions only, asked for levels |
