# Scenarios: action-log

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names. Commit the fixture state before a headless run, and name the object in the
prompt.

## Setup

- **no log**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md` copied as
  `PROJECT.md` with the `Action log` line removed; no `ACTIONS.md`.
- **declared**: `AGENTS.md` as above; `tests/fixtures/PROJECT.md`, `ACTIONS.md`, `TEAMS.md`, `TOOLS.md`,
  `TAILORING.md`, `RISKS.md`, `STAKEHOLDERS.md`, `CHANGES.md` and `GATES.md` copied at the root.
- **no tool**: as declared, with `TOOLS.md` listing no `issues` tool.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

The fixture is dated around 2026-11-23: for the backlog cases, tell the skill that today is 2026-11-23.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| setup-proposes-log-and-line | no log | "Set up the action log" | Proposes `ACTIONS.md` with the title only and the line `- Action log: \`ACTIONS.md\`` under Registers; writes after the user agrees; both files validate |
| add-asks-only-missing | declared | "Add an action: send the revised plan to the client" | Asks for owner and due date (not for what is given); proposes AC-006 with Status open, Raised today and Source; shows before writing; the file validates |
| we-is-not-an-owner | declared | "Add an action: we have to update the user guide by Friday" | Asks who owns it; turns "Friday" into a date and shows it for confirmation |
| one-home-risk-review | declared | "Add an action: review R-001 on 2026-12-01" | Records nothing: the review date lives in `RISKS.md`; says so and offers `/pm-skills:risk-register` |
| one-home-change-request | declared | "Add an action: assess the dark mode request" | Records nothing: CR-003 is `proposed` in `CHANGES.md`; points to `/pm-skills:change-request` |
| one-home-delivery-work | declared | "Add an action: implement the CSV export for credit notes" | Says delivery work belongs in the issues tool or the schedule; offers to create the item only if Jira is in write mode, after confirmation |
| handoff-from-minutes | declared | A handoff proposal block for two actions from minutes (one without owner) | Treats it as input: asks for the missing owner, computes AC-006 and AC-007, shows, writes on agreement, validates, reports the IDs |
| link-work-item | declared | "Create a Jira item for AC-002 and link it" | Proposes the item, creates it only after confirmation, records `Tool: Jira` and the key `Item` on AC-002; with no tool, gives the text and records nothing |
| align-with-tool | declared | "Review the open actions" | For AC-003 reads ACME-142 through the issues tool, proposes `done` with `Closed` if the item is done, and never edits the item; says what it could not read |
| backlog-pm | declared | "What do I have to do? Today is 2026-11-23" | Runs `pm_backlog.py`; prints the table unchanged and in order (AC-002, G-002, AC-004, S-001, CR-002, CR-003); points to the keepers for G, S and CR items without editing them |
| backlog-horizon-italian | declared | "Mostra il mio backlog di project manager per i prossimi 7 giorni. Oggi è 2026-11-23" | Answers in Italian with `--days 7`; overdue and undated items stay; uses the glossary terms |
| backlog-other-owner | declared | "Open actions for ada-l" | Runs with `--owner ada-l`; no change requests or gates in the table |
| drop-keeps-row | declared | "Drop AC-004, the client will announce it themselves" | Sets Status `dropped` with `Closed` and an `Outcome`; deletes nothing; the file validates |
| no-project-register | no project | "Add an action" | Suggests `/pm-skills:project-setup`; goes on only on a path the user names; invents no configuration |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-26 | 1.6.0 | add-asks-only-missing, backlog-pm, backlog-horizon-italian | partial | headless, sonnet, writes disallowed: the skill loaded in add and backlog. Add: asked owner and due date, proposed AC-006, wrote nothing. Backlog: ran `pm_backlog.py` and kept the order, pointed G-002, S-001, CR-002, CR-003 to their keepers; but ran it without `--today`, so Days used the session clock (not 2026-11-23) and the model flagged the mismatch (SKILL.md does not mention `--today`). Italian prompt "Cosa devo fare nei prossimi 7 giorni?" without an object: the skill never loaded, a generic answer from the registers; with "Mostra il mio backlog di project manager (le azioni aperte) per i prossimi 7 giorni" it loaded and used `--days 7 --today 2026-11-23` after `--help`, answered in Italian |
| 2026-11-26 | 1.6.0 | backlog-pm, backlog-horizon-italian (re-run after fixes) | pass | headless, sonnet: skill loaded in both; `pm_backlog.py PROJECT.md --today 2026-11-23` (Days 2, 4, 9, 22, table as printed, keepers named for G, S, CR items) and, in Italian with the README prompt, `--days 7 --today 2026-11-23` with overdue and undated items kept; both still mention the session clock says 11-26, harmless |
