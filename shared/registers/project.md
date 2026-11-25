# Project register format (`PROJECT.md`)

The project register holds a project's configuration: who it is for, how it is delivered, how its documents are
named and which other registers it keeps. `project-setup` builds and reviews it; every other skill reads it.

A project declares it with one line in its `AGENTS.md` (or `CLAUDE.md`), and declares nothing else there:

```markdown
- Project register: `PROJECT.md`
```

The path is relative to the project root, and so are the paths inside the register. Text after the closing backtick
is ignored, and so is a line inside a fenced code block, which is an example.

## Example

```markdown
# Project

## Identity

- Client: Acme Corp
- Project name: Acme Portal
- Internal code: ACME
- Client code: AC-2026-14
- Start date: 2026-01-12
- Planned end date: 2026-12-18
- Contract type: time and materials
- Deliverable language: English

## Profile

- Delivery approach: hybrid
- Reporting cadence: biweekly
- Agile framework: scrum
- Sprint length: 2
- Definition of Done: `docs/definition-of-done.md`

## Conventions

- Naming: coded
- Type codes: status-report=SAL
- Version in file name: no

## Registers

- Tools register: `TOOLS.md`
- Team register: `TEAMS.md`
- Tailoring register: `TAILORING.md`
- Risk register: `RISKS.md`
- Decision log: `DECISIONS.md`
- Stakeholder register: `STAKEHOLDERS.md`
- Capacity register: `CAPACITY.md`
- Change log: `CHANGES.md`
- Budget register: `BUDGET.md`
- Schedule register: `SCHEDULE.md`
```

Headings and keys are schema keys: they stay in English whatever the language of the values.

## Keys

Every key is optional: the register grows over one or more sessions, and a key is left out until its value is known.

| Section | Key | Rule |
|---|---|---|
| Identity | `Client` | free text; the organization the project is delivered to |
| Identity | `Project name` | free text |
| Identity | `Internal code` | 2 to 10 capital letters or digits, starting with a letter; the `<PROJ>` of coded names |
| Identity | `Client code` | free text; the client's reference for the project |
| Identity | `Start date`, `Planned end date` | `YYYY-MM-DD`; the end not before the start |
| Identity | `Contract type` | `fixed price`, `time and materials` or `internal` |
| Identity | `Deliverable language` | free text; the language documents are written in |
| Profile | `Delivery approach` | `predictive`, `agile` or `hybrid` |
| Profile | `Reporting cadence` | free text, usually `weekly`, `biweekly` or `monthly` |
| Profile | `Agile framework` | free text, usually `scrum` or `kanban` |
| Profile | `Sprint length` | a number of weeks, 1 to 8 |
| Profile | `Definition of Done` | the path, between backticks, of the project's Definition of Done |
| Profile | `Definition of Workflow` | the path, between backticks, of the project's Kanban Definition of Workflow |
| Conventions | `Naming` | `by date` or `coded` (see `shared/documents/common.md`); `coded` needs `Internal code` |
| Conventions | `Type codes` | comma-separated `<document type>=<CODE>`, overriding the plugin's default codes |
| Conventions | `Version in file name` | `yes` or `no` (the default) |
| Registers | `Tools register`, `Team register`, `Tailoring register`, `Risk register`, `Decision log`, `Stakeholder register`, `Capacity register`, `Change log`, `Budget register`, `Schedule register` | the path of the register, between backticks; two registers never share a file |

## Rules

1. Allowed lines: the title `# Project`, blank lines, the four sections `## Identity`, `## Profile`,
   `## Conventions`, `## Registers` (all four, once each, in this order) and `- Key: value` entries under them.
   There are no free notes.
2. A key appears once, in its own section, with a value; an unknown key is an error.
3. No value holds an email address or a phone number.
4. A new key, or a new register, is added to this format by the pull request of the first skill that uses it.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/project_register.py" validate <path to PROJECT.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
The plugin's hooks validate the project register and every register it lists after each edit, and sum them up in
one line at the start of a session.
