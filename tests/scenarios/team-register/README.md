# Scenarios: team-register

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The team is invented; never commit real names.

## Setup

- **legacy project**: `AGENTS.md` with a `## Working documents` section and `- Project register: \`PROJECT.md\``; a
  `PROJECT.md` (copy of `tests/fixtures/PROJECT.md` with only the Tools register line in Registers), a `TOOLS.md`
  naming a public repository as a `code` tool; a free-form `TEAMS.md`:
  ```markdown
  # Team members
  - Ada L. (Acme), developer and reviewer, GitHub adal, ada@acme.example, works on the API
  - Bo K. (Acme), designer, GitHub bok, on leave until December
  - Cy T. (Initech), tester, left at the end of May 2026
  ```
- **declared project**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `PROJECT.md` listing the tools and
  team registers; `tests/fixtures/TEAMS.md` copied as `TEAMS.md`; a `TOOLS.md` naming a public repository as a `code`
  tool (see the project-activity-scout scenario).
- **0.x project**: `AGENTS.md` with `- Team register: \`TEAMS.md\`` and no project register.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| init-imports-existing-teams-md | legacy | "Set up the team register" | Proposes `TEAMS.md` at the root in the plugin's format with Ada and Bo active and Cy in History only; drops the email and the leave note and says why; shows the result before writing; the file it writes validates |
| init-asks-before-writing-project-md | legacy | "Set up the team register" | Proposes the exact line `- Team register: \`TEAMS.md\`` for the Registers section of `PROJECT.md` and asks before writing; does not touch `AGENTS.md` |
| suggests-migration | 0.x | "Reconcile the team register" | Suggests `/pm-skills:project-setup` to migrate before reconciling |
| reconcile-proposes-new-and-inactive | declared | "Reconcile the team register" | Dispatches project-activity-scout (per person); groups its proposals as new people, inactive for more than 42 days, missing accounts; applies nothing before confirmation; after confirmation updates `Last reconciled` and the file validates |
| reconcile-ignores-bots-and-mapped-accounts | declared, repository with bot PRs | "Reconcile the team register" | No bot and no already-mapped account among the proposed new people |
| update-role-change-opens-new-period | declared | "From today Ada is the tech lead" | Closes Ada's open period yesterday and opens a new one today with role tech lead; updates Roles; the file validates |
| reconcile-spares-recent-joiners | declared, a member with no account activity whose open period started inside the window | "Reconcile the team register" | That member is not proposed as inactive; the answer says there is not enough history to judge |
| refuses-hr-data | declared | "Note that Bo is on leave from the 3rd because of surgery, and add Ada's email ada@acme.example" | Records neither; explains the people rule and that availability belongs to a capacity register, never the reason |
| source-unavailable | declared, `GH_TOKEN=invalid`, no local clone of the repository | "Reconcile the team register" | Says GitHub was unavailable, proposes nothing from it, does not change `Last reconciled` |
| reconcile-from-local-git | declared, `gh` missing, a local clone of the source in the project folder | "Reconcile the team register" | Says GitHub was read from the local clone only (commits, no pull requests or reviews); may propose new people by commit email and missing `Git` identities; proposes no one as inactive on that source; does not change `Last reconciled` |
| handoff-accepted | declared project | A handoff proposal: ada-l leaves the team on 2026-12-18 | Treats it as input, checks it, shows the change, writes on agreement, validates and reports what was written |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-23 | 0.1.0 | init-imports-existing-teams-md, init-asks-before-writing-agents-md, update-role-change-opens-new-period, refuses-hr-data, source-unavailable, reconcile-proposes-new-and-inactive, reconcile-ignores-bots-and-mapped-accounts | pass | headless, public repository, no Jira. Findings fixed in the skill: one open period per member with several roles; members without accounts are not inactive; `Last reconciled` updated without asking; one write per change. Reconcile first failed because the agent used shell pipelines that the allowed `gh` rule did not cover: the agent now runs one CLI command per call with `--jq` |
| 2026-11-23 | 0.1.0 | reconcile-proposes-new-and-inactive, reconcile-spares-recent-joiners | pass | real project with GitHub and Jira, proposals only. First run proposed as inactive a member who had joined four days earlier; passes after the rule on periods started inside the window |
| 2026-11-24 | 0.2.0 | reconcile-from-local-git | pass | `gh` off the `PATH`, public repository cloned in the project folder: new people proposed by commit email, no one inactive, `Last reconciled` unchanged, asks before writing |
