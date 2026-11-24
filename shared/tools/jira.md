# Known pitfalls: Jira (`mcp:atlassian` or `cli:acli`)

Read by skills and agents that reach an `issues` tool on Jira, through an Atlassian MCP server or the `acli` CLI
(`acli jira workitem search --jql "<JQL>"`).

- **Account IDs, never display names.** People are matched by account ID. With the Atlassian MCP server, name the
  fields explicitly and use the full view: the compact view returns only display names and drops custom fields.
- **Every page.** Searches are paginated: read every page before counting.
- **Useful JQL** (`<KEY>` is the project in the tool's Scope, `<start>` the first day of the window):
  - open work of a person: `project = <KEY> AND assignee = "<accountId>" AND statusCategory != Done`
  - done in the window: `project = <KEY> AND assignee = "<accountId>" AND statusCategory = Done AND resolved >= "<start>"`
  - active in the window: `project = <KEY> AND (assignee = "<accountId>" OR reporter = "<accountId>") AND updated >= "<start>"`
  - created in the window: `project = <KEY> AND created >= "<start>"`; resolved: `... AND resolved >= "<start>"`
  - transition history: ask for the changelog (`expand=changelog`) only when a skill needs it; it is heavy.
- **Unmapped assignees.** Look at open work only (`assignee is not EMPTY AND statusCategory != Done AND updated >= "<start>"`):
  an issue someone else closed in the window says nothing about its assignee. Leave out app and automation accounts
  (account type `app`).
- **Writes.** Comments, assignments, transitions and edits only when the tool's `Mode` is `write`, after the user
  agreed to that exact write; a bulk change is confirmed on the itemized list.
