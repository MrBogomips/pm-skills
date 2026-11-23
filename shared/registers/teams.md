# Team register format (`TEAMS.md`)

The team register records who works on the project now and who worked on it before, with the accounts and areas
needed to assign work and pick reviewers. It is project data, not a personnel file.

A project declares where its register lives with one line in its `AGENTS.md` (or `CLAUDE.md`):

```markdown
- Team register: `TEAMS.md`
```

The path is relative to the project root. The default location is `TEAMS.md` at the root.

## Example

```markdown
# Team

Last reconciled: 2026-11-20
Sources: github:acme/web, github:acme/api, jira:ACME

## Active team

| Slug | Name | Organization | GitHub | Jira | Roles | Areas |
|---|---|---|---|---|---|---|
| ada-l | Ada L. | Acme | adal | 5b10ac8d82e05b22cc7d4ef5 | developer, reviewer | api, data model |
| cy-t | Cy T. | Initech | cyt |  | tester | web |

## History

| Slug | From | To | Role |
|---|---|---|---|
| ada-l | 2026-01-12 |  | developer |
| cy-t | 2026-03-01 | 2026-05-31 | tester |
| cy-t | 2026-09-01 |  | tester |
| di-r | 2026-01-12 | 2026-06-30 | analyst |
```

Headings and column names are schema keys: they stay in English whatever the language of the content.

## Fields

| Field | Meaning | Rule |
|---|---|---|
| `Last reconciled` | the last date the register was checked against its sources | optional; `YYYY-MM-DD` |
| `Sources` | where the team's activity is read from | optional; comma-separated `github:<owner>/<repo>` or `jira:<PROJECT KEY>` |
| `Slug` | a stable identifier for the person, used across both tables | lowercase letters, digits, single hyphens; unique in Active team |
| `Name` | the name the team uses | not empty |
| `Organization` | the company the person works for (own, supplier, client) | free text |
| `GitHub` | GitHub login | empty, or a login without `@` |
| `Jira` | Jira account ID (stable, unlike display names) | empty, or one token with no spaces and no `@` |
| `Roles` | the person's roles on the project | comma-separated, at least one |
| `Areas` | what the person knows and can review: repositories, modules, kinds of work | comma-separated, may be empty |
| `From`, `To` | a period on the project; `To` empty while it is open | `YYYY-MM-DD`; `From` not after `To` |
| `Role` | the role held in that period | free text |

## Rules

1. Allowed lines: the title `# Team`, blank lines, `Last reconciled:`, `Sources:`, the section `## Active team`
   followed by its table, then the section `## History` followed by its table. Anything else is an error: there are
   no free notes in the register.
2. Table headers are exactly the ones in the example, in that order.
3. Every member of Active team has exactly one open period in History.
4. An open period belongs to a member of Active team; former members have only closed periods.
5. The periods of one person never overlap. A person who leaves and comes back has two periods.
6. A role change closes the current period and opens a new one on the same day it takes effect.
7. No cell holds an email address; no cell other than `Jira`, `From` and `To` holds a phone number.

## What does not belong here

Contacts (email, phone), allocation percentages, availability and leave, reporting lines, appraisals, notes on
motivation or performance, and anything else of human resources management. If someone asks to record such data,
explain that the register holds project data only and leave it out.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/teams_register.py" validate <path to TEAMS.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
In projects that declare the register, the plugin's hook also validates it after every edit.
