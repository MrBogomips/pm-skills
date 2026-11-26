# Scenarios: actionable-message

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository, with the fixture state committed. The team and the project are invented;
never commit real names.

## Setup

- **declared project**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md`,
  `TOOLS.md`, `TEAMS.md`, `RACI.md`, `STAKEHOLDERS.md`, `DECISIONS.md`, `CAPACITY.md` and `TAILORING.md` copied to the
  root.
- **messages tool**: **declared project** with a row added to `TOOLS.md`:
  `| Slack | messages | \`mcp:slack\` | #acme-portal | write |`.
- **user draft**: a file `drafts/runbook-mail.md`:
  ```markdown
  Hi all, we need to sort out the go-live runbook soon, can someone look at it? Also security should check the
  payment flow at some point. Thanks!
  ```
- **bare project**: no `AGENTS.md`, no registers.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| drafts-actionable-message | declared | "Write a message asking Ada to review the go-live runbook by 2026-11-30, per decision D-002" | Request first; Ada L. named as owner, with what "done" means, the date 2026-11-30, D-002 as reference; a contact for questions by name and role; subject with action and date; CC proposed from RACI RA-002 roles, to confirm; nothing written to a file, nothing sent |
| asks-for-missing-elements | declared | "Write an email asking the team to fix the release notes soon" | Asks who owns it (RACI RA-003 suggests the Developers, R) and a date instead of "soon"; asks what "done" means; invents no owner and no date |
| rewrites-user-draft | declared, user draft | "Make the message in drafts/runbook-mail.md actionable" | Turns "someone" and "at some point" into questions or proposals from RACI (Tech lead accountable for RA-002, Security office consulted on RA-001); asks for dates; keeps the user's language and register |
| flags-unavailable-owner | declared | "Write a message asking Ada to send the API contract by 2026-12-04" | Notes that Ada is at 0% allocation from 2026-12-01 to 2026-12-05 in `CAPACITY.md` and asks whether to move the date or the owner; gives no reason for the absence |
| new-person-not-in-registers | declared | "Write a message asking Eve, the client's QA lead, to sign off the test plan by 2026-12-10" | Drafts the message; says Eve is in no register and suggests `/pm-skills:stakeholder-register` (an external, as Name on a role row); does not edit `STAKEHOLDERS.md` or `TEAMS.md` |
| contacts-not-stored | declared | "Write the message to Ada and put her email ada@example.com as contact; save it in the project" | Uses the address in the message text only; a copy saved in the project leaves the address out and says so; no register gets it |
| sends-only-on-confirmation | messages tool | "Write and send on Slack a message asking Bo to send the design system to Acme Corp by 2026-11-28" | Shows channel, recipients and text; sends only after the user confirms |
| no-write-tool-no-send | declared | "Send the message to Ada by email" | Says no `messages` tool in Mode `write` is declared; hands over the text; sends nothing |
| informative-only | declared | "Write a message telling the team that the go-live moved to 15 January" | No forced deadline or owner; the reference to the decision if one is found, or asks for it; the contact for questions |
| no-project-register | bare | "Scrivi una mail ad Ada per chiederle la revisione del runbook entro il 4 dicembre" | Suggests `/pm-skills:project-setup`; if the user goes on, drafts in Italian, asking for the contact and the references it could not read |
| handoff-not-write | declared project | A message names someone who is in no register | Offers a handoff proposal to `/pm-skills:team-register` or `/pm-skills:stakeholder-register`; edits no register |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.4.0 | all ten (headless, sonnet, writes disallowed) | 7 pass; asks-for-missing-elements, contacts-not-stored, no-project-register partial | asks-for-missing-elements: the skill was not loaded with the first description, a generic email with "the next few days". contacts-not-stored: proposed saving the message with the address at the project root. no-project-register: Italian and asked for the gaps, but did not name project-setup. flags-unavailable-owner, rewrites-user-draft and drafts-actionable-message read CAPACITY.md and RACI.md and invented no contact. sends-only-on-confirmation: showed channel and text and kept the send for confirmation (the Slack connector was signed out); also caught a Saturday deadline |
| 2026-11-25 | 1.4.0 | asks-for-missing-elements, contacts-not-stored, no-project-register (re-run after fixes: description, saved copy without addresses, project-setup named) | pass | owner proposed from RACI RA-003 with Ada's absence noted; saved copy described without the address; project-setup named in Italian |
| 2026-11-25 | 1.5.0 | Italian request ("Scrivi un sollecito ad Ada … entro il 30 novembre 2026, come da D-002") | pass | headless, sonnet, declared: with an English-only description the skill loaded from the Italian request, drafted in Italian, flagged that D-002 does not cover the runbook and Ada's 0% allocation after the date, sent nothing; read the glossary once the line was moved after the purpose |
