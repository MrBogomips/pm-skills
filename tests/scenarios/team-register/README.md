# Scenarios: team-register

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The team is invented; never commit real names.

## Setup

- **legacy project**: `AGENTS.md` with a `## Working documents` section and no `Team register:` line; a free-form
  `TEAMS.md`:
  ```markdown
  # Team members
  - Ada L. (Acme), developer and reviewer, GitHub adal, ada@acme.example, works on the API
  - Bo K. (Acme), designer, GitHub bok, on leave until December
  - Cy T. (Initech), tester, left at the end of May 2026
  ```
- **declared project**: `AGENTS.md` with `- Team register: \`TEAMS.md\`` and `tests/fixtures/TEAMS.md` copied as
  `TEAMS.md`, with `Sources:` pointing to a public repository (see the team-activity-scout scenario).

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| init-imports-existing-teams-md | legacy | "Set up the team register" | Proposes `TEAMS.md` at the root in the plugin's format with Ada and Bo active and Cy in History only; drops the email and the leave note and says why; shows the result before writing; the file it writes validates |
| init-asks-before-writing-agents-md | legacy | "Set up the team register" | Proposes the exact line `- Team register: \`TEAMS.md\``, placed in Working documents, and asks before writing `AGENTS.md` |
| reconcile-proposes-new-and-inactive | declared | "Reconcile the team register" | Dispatches team-activity-scout; groups its proposals as new people, inactive for more than 42 days, missing accounts; applies nothing before confirmation; after confirmation updates `Last reconciled` and the file validates |
| reconcile-ignores-bots-and-mapped-accounts | declared, repository with bot PRs | "Reconcile the team register" | No bot and no already-mapped account among the proposed new people |
| update-role-change-opens-new-period | declared | "From today Ada is the tech lead" | Closes Ada's open period yesterday and opens a new one today with role tech lead; updates Roles; the file validates |
| reconcile-spares-recent-joiners | declared, a member with no account activity whose open period started inside the window | "Reconcile the team register" | That member is not proposed as inactive; the answer says there is not enough history to judge |
| refuses-hr-data | declared | "Note that Bo is on leave from the 3rd, and add Ada's email ada@acme.example" | Records neither; explains that the register holds project data only |
| source-unavailable | declared, `GH_TOKEN=invalid` | "Reconcile the team register" | Says GitHub was unavailable, proposes nothing from it, does not change `Last reconciled` |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-23 | 0.1.0 | init-imports-existing-teams-md, init-asks-before-writing-agents-md, update-role-change-opens-new-period, refuses-hr-data, source-unavailable, reconcile-proposes-new-and-inactive, reconcile-ignores-bots-and-mapped-accounts | pass | headless, public repository, no Jira. Findings fixed in the skill: one open period per member with several roles; members without accounts are not inactive; `Last reconciled` updated without asking; one write per change. Reconcile first failed because the agent used shell pipelines that the allowed `gh` rule did not cover: the agent now runs one CLI command per call with `--jq` |
| 2026-11-23 | 0.1.0 | reconcile-proposes-new-and-inactive, reconcile-spares-recent-joiners | pass | real project with GitHub and Jira, proposals only. First run proposed as inactive a member who had joined four days earlier; passes after the rule on periods started inside the window |
