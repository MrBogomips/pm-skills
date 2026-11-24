# Known pitfalls: GitHub (`cli:gh`)

Read by skills and agents that reach a tool declared with `Access: cli:gh`. Only what is not obvious from `gh help`.

- **One command per call.** Run one `gh` command per call, without pipes, `cd`, loops or other shell commands:
  projects often allow `gh` alone, and a pipeline stops on a permission prompt. Filter output with `--jq`.
- **Call it by name.** If `gh` is not on the `PATH`, it is missing: do not look for it elsewhere. Check
  `gh auth status` first; a failure is `auth expired` or `unavailable`, never zero activity.
- **Search rate limit.** GitHub allows about 30 search requests a minute. Cover several repositories in one search by
  repeating `--repo`, and take everything needed from one search of the window:
  `gh search prs --repo <r1> --repo <r2> --updated ">=<start>" --json author,repository,number,createdAt,updatedAt,closedAt,state --limit 1000`.
  Reviews need one search per person: `--reviewed-by <login>`.
- **Truncation.** A search that returns exactly 1000 results was cut short: split the window in two and run it for
  each half.
- **Bots.** Leave out logins ending in `[bot]` and authors whose `is_bot` is true or whose `type` is `Bot`.
- **Fallback.** When a search fails (rate limit, a repository `gh` cannot reach), read that source from a local clone
  (`shared/tools/git.md`) and report no counts from the failed search, never zeros.
- **Writes.** Only when the tool's `Mode` is `write`, after the user agreed to that exact write: for example
  `gh pr edit <n> --repo <owner>/<repo> --add-reviewer <login>`.
