# Scenarios: project-activity-scout

Manual checks of the agent, run with `claude --plugin-dir <repo>` (or `claude -p --plugin-dir <repo> "<prompt>"`)
in a throwaway project. Never commit real names: the registers below are built at run time.

## Setup

1. Pick a public GitHub repository with several pull requests in the last 42 days.
2. In a throwaway folder (a git repository), clone that repository for cases g and h
   (`git clone --filter=blob:none` is enough), and write:
   - `AGENTS.md` with `- Project register: \`PROJECT.md\``;
   - `PROJECT.md` listing `TOOLS.md` and `TEAMS.md` in its Registers section;
   - `TOOLS.md` with the repository as a `code` tool (`cli:gh`, Scope `<owner>/<repo>`, `read`), plus a Jira `issues`
     tool for cases e and f;
   - a valid `TEAMS.md` whose Active team maps **two** of the repository's recent pull request authors (GitHub
     column), plus one invented member with no GitHub account.
3. Prompts: "Use the project-activity-scout agent on PROJECT.md, per person, window 42 days, all members." and
   "Use the project-activity-scout agent on PROJECT.md, per project, window 14 days."

## Cases

| Case | Condition | Expected |
|---|---|---|
| a. per person | `gh` authenticated; no Jira tool | One row per active member; the two mapped authors have PR counts and a last activity date; the invented member has `n/a` for GitHub; `Unmapped accounts` lists other recent authors; `Sources checked` says `ok` for the tool |
| b. tool unavailable | run with `GH_TOKEN=invalid`, no clone | `Sources checked` says `auth expired` or `unavailable: <reason>`; GitHub columns are `n/a`; no invented numbers |
| c. bots | the repository has bot pull requests (e.g. `dependabot[bot]`) in the window | no bot login in `Unmapped accounts` |
| d. read only | any of the above, with the tool declared `write` | the agent ran only reading commands: no review, comment, edit or issue change |
| e. Jira unmapped | a Jira tool with an assignee active in the window who is not in the register | `Unmapped accounts` gives that assignee's Jira account ID, not only the display name; app accounts are left out |
| f. Jira bulk closure | an account outside the register whose issues were only closed by someone else in the window | that account is not in `Unmapped accounts` |
| g. local git fallback | `gh` missing (a `PATH` without it); the project folder holds a clone; one mapped member has their commit email in `Git`, another only a GitHub login with no-reply commits | `Sources checked` says `local git` with the clone's path and the date of its newest commit; `Commits` and `Repos touched` from the clone; PR columns `n/a`; unmapped commit authors by email, no bots; no `git fetch`, `pull` or other writing command |
| h. no local clone | as g, with no clone | the source is `unavailable: <reason>`; GitHub columns and `Commits` are `n/a` |
| i. per project | `gh` authenticated | `Code` gives merged and open pull requests for the repository; `Releases` lists the releases of the window or `none`; `Issues`, `Incidents`, `CI` say `n/a` when no such tool is declared; `Sources checked` closes the report |
| j. no tools register | `PROJECT.md` without a Tools register line | says there is no tools register and stops |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-23 | 0.1.0 (as team-activity-scout) | a, b, c, d, e, f | pass | public repository and a real project with Jira through the Atlassian MCP server; fixes: bot rule on `is_bot`/`type`, one search for the window, Jira account IDs from the full view, unmapped Jira assignees from open work only |
| 2026-11-24 | 0.2.0 (as team-activity-scout) | c, d, g, h | pass | local git fallback with `gh` off the `PATH`; counts from `shortlog -sne` match a script |
