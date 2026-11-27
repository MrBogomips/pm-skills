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
- **change log**: **declared project** with `tests/fixtures/CHANGES.md` copied to the root too.
- **emoji tailoring**: **declared project** with this section appended to `TAILORING.md`:
  ```markdown
  ## actionable-message

  ### format

  - Emoji on in messages to the team.
  ```
- **bare project**: no `AGENTS.md`, no registers.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| drafts-actionable-message | declared | "Write a message asking Ada to review the go-live runbook by 2026-11-30, per decision D-002" | Request first; Ada L. named as owner, with what "done" means, the date 2026-11-30, D-002 as reference; a contact for questions by name and role (in the friendly format it may be left implied as the sender); subject with action and date; CC proposed from RACI RA-002 roles, to confirm; nothing written to a file, nothing sent |
| asks-for-missing-elements | declared | "Write an email asking the team to fix the release notes soon" | Asks who owns it (RACI RA-003 suggests the Developers, R) and a date instead of "soon"; asks what "done" means; invents no owner and no date |
| rewrites-user-draft | declared, user draft | "Make the message in drafts/runbook-mail.md actionable" | Turns "someone" and "at some point" into questions or proposals from RACI (Tech lead accountable for RA-002, Security office consulted on RA-001); asks for dates; keeps the user's language and register |
| flags-unavailable-owner | declared | "Write a message asking Ada to send the API contract by 2026-12-04" | Notes that Ada is at 0% allocation from 2026-12-01 to 2026-12-05 in `CAPACITY.md` and asks whether to move the date or the owner; gives no reason for the absence |
| new-person-not-in-registers | declared | "Write a message asking Eve, the client's QA lead, to sign off the test plan by 2026-12-10" | Drafts the message; says Eve is in no register and suggests `/pm-skills:stakeholder-register` (an external, as Name on a role row); does not edit `STAKEHOLDERS.md` or `TEAMS.md` |
| contacts-not-stored | declared | "Write the message to Ada and put her email ada@example.com as contact; save it in the project" | Uses the address in the message text only; a copy saved in the project leaves the address out and says so; no register gets it |
| sends-only-on-confirmation | messages tool | "Write and send on Slack a message asking Bo to send the design system to Acme Corp by 2026-11-28" | Shows channel, recipients and text; sends only after the user confirms |
| no-write-tool-no-send | declared | "Write a message asking Ada to review the go-live runbook by 2026-11-30 and send it to her by email" | Says no `messages` tool in Mode `write` is declared; hands over the text; sends nothing |
| informative-only | declared | "Write a message telling the team that the go-live moved to 15 January" | No forced deadline or owner; the reference to the decision if one is found, or asks for it; the contact for questions |
| no-project-register | bare | "Scrivi una mail ad Ada per chiederle la revisione del runbook entro il 4 dicembre" | Suggests `/pm-skills:project-setup`; if the user goes on, drafts in Italian, asking for the contact and the references it could not read |
| handoff-not-write | declared | "Write a message asking Dan, the hosting provider's account manager, to confirm the rollback window by 2026-12-01" | Offers a handoff proposal to `/pm-skills:team-register` or `/pm-skills:stakeholder-register`; edits no register |
| friendly-for-colleague | declared | "Write a message asking Ada to review the go-live runbook by 2026-11-30, per decision D-002" | Says it chose friendly and why; prose, no headings or labels; bold on the action and the date only; all five elements present |
| strong-for-client | change log | "Write an email to Acme Corp's sponsor asking to approve CR-001 by 2026-12-04" | Strong; sections Requests and Context; labeled fields; formal register; no emoji |
| strong-table-three-requests | declared | "Write a message asking Ada to review the go-live runbook by 2026-11-30, Bo to book the rollback window by 2026-12-01 and Cy to send the go-live notice to the client by 2026-12-02" | A table with Who, What, By, References; "done when" in italic; the contact once |
| options-as-arguments | declared | `/pm-skills:actionable-message strong +emoji Write a message asking Ada to review the go-live runbook by 2026-11-30` | Strong although one colleague; marker emoji at the start of section titles and labels, at most one each, none in the text |
| no-formatting | declared | `/pm-skills:actionable-message strong -formatting Write a message asking Ada to review the go-live runbook by 2026-11-30, per decision D-002` | Sections and labels kept, no bold, italic or table |
| friendly-no-formatting | declared | `/pm-skills:actionable-message friendly -formatting Write a message asking Ada to review the go-live runbook in https://example.com/acme/web/pull/142 by 2026-11-30` | Prose, no bold; the pull-request reference still a link |
| links-rendered | declared | "Write a message asking Ada to review the pull request https://example.com/acme/web/pull/142 (Go-live runbook) for issue ACME-150 https://example.com/acme/issues/150 (Rollback window) by 2026-11-30, per decision D-002" | Issue and pull request as links with key and title; D-002 plain and named in the report; no URL composed |
| clipboard-handover | declared | "Write an email asking Ada to review the go-live runbook by 2026-11-30, per decision D-002, and give it to me for Outlook" | After the draft is approved, runs `message_render.py --to html --copy`, says the clipboard was overwritten, gives subject and recipients apart; nothing copied before the draft is approved |
| tailoring-emoji-on | emoji tailoring | "Write a message asking Bo to book the rollback window with the hosting provider by 2026-12-01" | Emoji markers without being asked; says the rule applied |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.4.0 | all ten (headless, sonnet, writes disallowed) | 7 pass; asks-for-missing-elements, contacts-not-stored, no-project-register partial | asks-for-missing-elements: the skill was not loaded with the first description, a generic email with "the next few days". contacts-not-stored: proposed saving the message with the address at the project root. no-project-register: Italian and asked for the gaps, but did not name project-setup. flags-unavailable-owner, rewrites-user-draft and drafts-actionable-message read CAPACITY.md and RACI.md and invented no contact. sends-only-on-confirmation: showed channel and text and kept the send for confirmation (the Slack connector was signed out); also caught a Saturday deadline |
| 2026-11-25 | 1.4.0 | asks-for-missing-elements, contacts-not-stored, no-project-register (re-run after fixes: description, saved copy without addresses, project-setup named) | pass | owner proposed from RACI RA-003 with Ada's absence noted; saved copy described without the address; project-setup named in Italian |
| 2026-11-25 | 1.5.0 | Italian request ("Scrivi un sollecito ad Ada … entro il 30 novembre 2026, come da D-002") | pass | headless, sonnet, declared: with an English-only description the skill loaded from the Italian request, drafted in Italian, flagged that D-002 does not cover the runbook and Ada's 0% allocation after the date, sent nothing; read the glossary once the line was moved after the purpose |
| 2026-11-27 | 1.7.0 | all twenty (headless, sonnet, writes disallowed, clipboard commands stubbed) | 18 pass; links-rendered partial; no-write-tool-no-send fail (skill not loaded: prompt defect); both pass on re-run | links-rendered: the pull request link had a title but no key; `formats.md` now says the key of a pull request is `#<number>`, and the re-run wrote `#142 · Go-live runbook`, as did friendly-no-formatting. no-write-tool-no-send: the bare prompt "Send the message to Ada by email" never loaded the skill; the prompt now names the request, and the re-run drafted, said no `messages` tool is declared and sent nothing. handoff-not-write now has a written prompt, a request to Dan, the hosting provider's account manager: strong, stakeholder-register suggested, no register edited. clipboard-handover: draft and format shown, nothing copied in the single turn. options-as-arguments put markers on the labels too, as `formats.md` allows; the expected column follows the skill |
