# Scenarios: flow-data-scout

Manual checks of the agent, run with `claude --plugin-dir <repo>` (or `claude -p --plugin-dir <repo> "<prompt>"`)
in a throwaway project. Never commit real names: the registers below are built at run time.

## Setup

1. A Jira project (or a public GitHub repository with issues moved through project columns) with items that changed
   status in the last 90 days.
2. In a throwaway folder (a git repository), write:
   - `AGENTS.md` with `- Project register: \`PROJECT.md\``;
   - `PROJECT.md` listing `TOOLS.md` in its Registers section;
   - `TOOLS.md` with the tracker as an `issues` tool (Scope the project or repository, `read`).
3. Prompt: "Use the flow-data-scout agent on PROJECT.md, window 90 days, all item types."

## Cases

| Case | Condition | Expected |
|---|---|---|
| a. snapshot shape | tracker reachable | One fenced `csv` block with the header `item,type,state,entered_at` exactly; rows ordered by item then time; ISO 8601 timestamps; the CSV passes `flow_data.py validate` once saved by the caller |
| b. no people | items have assignees and reporters | No assignee, reporter, name or account anywhere in the output |
| c. history before the window | an item started before the window and finished inside it | Its earlier transitions are included |
| d. coverage | any | `Coverage` gives the window, scope, item and row counts, types found and every status with its row count |
| e. tool unavailable | invalid credentials | `Sources checked` says `auth expired` or `unavailable: <reason>`; no rows; no invented data |
| f. read only | the tool declared `write` | Only reading calls; no transition, comment or edit; no file written |
| g. no issues tool | `TOOLS.md` with no `issues` purpose | Says so and stops |
| h. pagination | more items than one page of results | Every page read; counts match the tracker |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
