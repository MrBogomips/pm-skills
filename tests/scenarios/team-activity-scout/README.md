# Scenarios: team-activity-scout

Manual checks of the agent, run with `claude --plugin-dir <repo>` (or `claude -p --plugin-dir <repo> "<prompt>"`)
in a throwaway project. Never commit real names: the register below is built at run time.

## Setup

1. Pick a public GitHub repository with several pull requests in the last 42 days.
2. In a throwaway folder, write `AGENTS.md` with `- Team register: \`TEAMS.md\`` and a valid `TEAMS.md` whose
   `Sources:` line names that repository and whose Active team maps **two** of its recent pull request authors
   (GitHub column), plus one invented member with no GitHub account.
3. Prompt: "Use the team-activity-scout agent on TEAMS.md, window 42 days, all members."

## Cases

| Case | Condition | Expected |
|---|---|---|
| a. all sources | `gh` authenticated; no Jira source | One row per active member; the two mapped authors have PR counts and a last activity date; the invented member has `n/a` for GitHub; `Unmapped accounts` lists other recent authors; `Sources checked` says `ok` for the repository |
| b. GitHub unavailable | run with `GH_TOKEN=invalid` | `Sources checked` says `auth expired` or `unavailable: <reason>` for the repository; GitHub columns are `n/a`; no invented numbers |
| c. bots | the repository has bot pull requests (e.g. `dependabot[bot]`) in the window | no login ending in `[bot]` appears in `Unmapped accounts` |
| d. read only | any of the above | the agent ran only reading commands: no `gh pr review`, `gh pr comment`, `gh issue edit`, no Jira writes |
| e. Jira unmapped | a Jira source with an assignee active in the window who is not in the register | `Unmapped accounts` gives that assignee's Jira account ID, not only the display name; app and automation accounts are left out |
| f. Jira bulk closure | an account outside the register whose issues were only closed by someone else in the window (no open issues assigned) | that account is not in `Unmapped accounts` |

## Runs

| Date | Version | a | b | c | d | e, f | Notes |
|---|---|---|---|---|---|---|---|
| 2026-11-23 | 0.1.0 | pass | pass | pass (after the rule on `is_bot`/`type` was added: `Copilot` was kept before) | pass | – | public repository, no Jira source; Jira path not exercised |
| 2026-11-23 | 0.1.0 | pass | – | pass | pass | – | rerun after the review fix: one search for the window plus one review search per member (5 gh calls); same counts as before |
| 2026-11-23 | 0.1.0 | pass | – | pass | pass | pass | real project with Jira through the Atlassian MCP server: first run reported unmapped Jira assignees by display name only (the compact view drops account IDs); passes after asking for the assignee field in the full view |
| 2026-11-23 | 0.1.0 | pass | – | pass | pass | pass | real project, rerun: unmapped Jira assignees are read from open work only (f pass): two former members whose issues someone else closed in the window are no longer reported |
