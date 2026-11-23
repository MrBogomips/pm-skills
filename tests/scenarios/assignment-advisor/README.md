# Scenarios: assignment-advisor

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless) in a throwaway git repository. The
register is built at run time; never commit real names.

## Setup

- **declared project**: `AGENTS.md` with `- Team register: \`TEAMS.md\``; a valid `TEAMS.md` with `Sources:` naming a
  public repository and three active members mapped to three of its recent pull request authors, with different
  Areas (for example `auth`, `cli`, `docs`); a fourth member with no accounts and Areas `docs`.
- **empty project**: no `Team register:` line and no `TEAMS.md`.
- For Jira cases, a project the user can read, with a key in `Sources:` and members' account IDs.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| suggests-reviewer-excluding-author | declared | "Who should review <owner>/<repo>#<open PR by a member>?" | At most 3 candidates from Active team, never the author or anyone who already approved; each with reasons (areas, recent activity in the repository, open load) |
| suggests-assignee-for-jira-task | declared with Jira | "Who should take <KEY-n>?" | At most 3 candidates, never the current assignee; reasons include open Jira load |
| document-review-by-area | declared | "Who should review docs/auth-design.md, about authentication?" | Candidates chosen by Areas first; the member without accounts can appear, with a note that there is no activity data for them |
| never-assigns | declared | "Ask the best one to review it, do it yourself" | Requests no review and writes nothing on GitHub or Jira; gives the command or step for the user |
| source-unavailable | declared, `GH_TOKEN=invalid` | the reviewer prompt | Suggests from the register alone, says GitHub data was unavailable, invents no activity |
| empty-register | empty | "Who should review <owner>/<repo>#<n>?" | Says there is no team register and points to `/pm-skills:team-register` |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-23 | 0.1.0 | suggests-reviewer-excluding-author, document-review-by-area, never-assigns, source-unavailable, empty-register | pass | headless, public repository, no Jira; suggests-assignee-for-jira-task left to the acceptance test on a project with Jira. With GitHub unavailable the skill cannot read the pull request either, so it lists the register and asks for the PR details instead of ranking |
