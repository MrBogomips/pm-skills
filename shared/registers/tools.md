# Tools register format (`TOOLS.md`)

The tools register lists the systems a project uses, what each is for, how it is reached and whether skills may
write to it. Skills ask for a capability (`issues`, `code`, `publish`) and use the tools that offer it; they never
name a tool. `project-setup` builds and reviews the register; it is declared in the Registers section of
`PROJECT.md` as `` - Tools register: `TOOLS.md` ``.

## Example

```markdown
# Tools

| Tool | Purpose | Access | Scope | Mode |
|---|---|---|---|---|
| Jira | issues | `mcp:atlassian` | project ACME | write |
| GitHub | code, ci, releases | `cli:gh` | acme/web, acme/api | read |
| Plan | schedule, costs | `file:plan/acme-schedule.xlsx` | baseline and actuals | read |
| Word | publish | `skill:acme-docx` | status-report → docx | write |
```

## Columns

| Column | Meaning | Rule |
|---|---|---|
| `Tool` | the name the team uses for the system | not empty |
| `Purpose` | the capabilities the tool offers | comma-separated, from the vocabulary below |
| `Access` | how the tool is reached | `<kind>:<target>`, optionally between backticks |
| `Scope` | what the tool covers: a Jira project, repositories, the content of a file; for `publish`, the document type and the format it produces (`status-report → docx`) | not empty |
| `Mode` | `read`, or `write` when skills may write through it | `read` or `write` |

**Purpose vocabulary**

| Capability | What it gives |
|---|---|
| `issues` | work items, their status, assignees and transition history (Jira, GitHub Issues, Linear) |
| `code` | repositories, pull requests, reviews and commits |
| `ci` | builds, pipelines and their outcomes |
| `releases` | releases, tags and deployments |
| `incidents` | incidents and their resolution |
| `schedule` | plans, milestones, baselines |
| `costs` | budget, actual costs, rates per role |
| `documents` | a document store (wiki, shared drive) |
| `meetings` | meeting notes, transcripts and action items |
| `messages` | chat or email channels |
| `calendar` | the project calendar |
| `publish` | a renderer that turns a Markdown deliverable into a distribution format |

**Access kinds**

| Kind | Target | Example |
|---|---|---|
| `mcp` | the name of an MCP server connected to the session | `mcp:atlassian` |
| `cli` | a command-line tool on the `PATH` | `cli:gh` |
| `file` | a path relative to the project root; office files are read with the session's document conversion | `file:plan/acme-schedule.xlsx` |
| `skill` | a skill available in the session | `skill:acme-docx` |
| `script` | a script, with its path relative to the project root | `script:tools/render.sh` |
| `artifact` | an artifact renderer of the `pm-artifacts` plugin | `artifact:status-dashboard` |

## Rules

1. Allowed lines: the title `# Tools`, blank lines and the table. There are no free notes.
2. The header is exactly the one in the example.
3. No two rows have the same tool, access and scope.
4. No cell holds an email address: credentials and contacts never go here. Access says how to reach a tool, never a
   secret.

## How skills use it

- A skill names the capability and the data it needs, picks the tools with that `Purpose`, and reaches each through
  its `Access` with the model's and the tool's own abilities. Known pitfalls of a specific tool are in
  `${CLAUDE_PLUGIN_ROOT}/shared/tools/<tool>.md` when the plugin has them.
- `Mode` governs writes to the tool's own system (an issue, a comment, a sent email, an upload). A renderer that only
  produces a file in the project works in either mode, after the user agrees to the output path.
- A skill writes to a tool only when its `Mode` is `write`, shows each write first and makes it only after the user
  agrees; a bulk operation is confirmed on the itemized list. Collector agents never write.
- A tool that cannot be reached is reported as unavailable, with the reason; nothing is guessed in its place.
- With no tools register, a skill suggests `/pm-skills:project-setup` and names the sources it could not read.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/tools_register.py" validate <path to TOOLS.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
