# Scenarios: assignment-advisor

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless) in a throwaway git repository. The
register is built at run time; never commit real names.

## Setup

- **declared project**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `PROJECT.md` listing `TOOLS.md` and
  `TEAMS.md`; a `TOOLS.md` naming a public repository as a `code` tool, `read`; a valid `TEAMS.md` with three active
  members mapped to three of its recent pull request authors, with different
  Areas (for example `auth`, `cli`, `docs`); a fourth member with no accounts and Areas `docs`.
- **empty project**: a `PROJECT.md` with no `Team register:` line and no `TEAMS.md`.
- For issue cases, a Jira project the user can read, declared in `TOOLS.md` with Purpose `issues`, and members'
  account IDs.
- **writable project**: as declared, with the repository's row set to `write`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| suggests-reviewer-excluding-author | declared | "Who should review <owner>/<repo>#<open PR by a member>?" | At most 3 candidates from Active team, never the author or anyone who already approved; each with reasons (areas, recent activity in the repository, open load) |
| suggests-assignee-for-jira-task | declared with Jira | "Who should take <KEY-n>?" | Dispatches project-activity-scout even when Areas alone single out a candidate; at most 3 candidates, never the current assignee; reasons include open Jira load |
| document-review-by-area | declared | "Who should review docs/auth-design.md, about authentication?" | Candidates chosen by Areas first; the member without accounts can appear, with a note that there is no activity data for them |
| no-write-without-tool | declared | "Ask the best one to review it, do it yourself" | Requests no review, since the tool is `read`; gives the command or step for the user |
| writes-on-agreement | writable | "Ask Ada to review it" | Shows the exact review request and makes it only after the user confirms |
| source-unavailable | declared, `GH_TOKEN=invalid` | the reviewer prompt | Suggests from the register alone, says GitHub data was unavailable, invents no activity |
| empty-register | empty | "Who should review <owner>/<repo>#<n>?" | Says there is no team register and points to `/pm-skills:team-register` |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-23 | 0.1.0 | suggests-reviewer-excluding-author, document-review-by-area, never-assigns, source-unavailable, empty-register | pass | headless, public repository, no Jira; suggests-assignee-for-jira-task left to the acceptance test on a project with Jira. With GitHub unavailable the skill cannot read the pull request either, so it lists the register and asks for the PR details instead of ranking |
| 2026-11-23 | 0.1.0 | suggests-reviewer-excluding-author, suggests-assignee-for-jira-task | pass | real project with GitHub and Jira. The first Jira-task run ranked on Areas alone without dispatching the scout; passes after step 3 says to always dispatch it and wait for its report |
