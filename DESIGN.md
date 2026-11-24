# Design guidelines

The goals, principles and patterns behind every skill, agent and hook of `pm-skills`. Read this file before adding
or changing one. `AGENTS.md` holds the operational rules (layout, confidentiality, version, verification); this file
says what to build and why. A rule lives in one of the two files, never in both.

The components published today (`team-register`, `assignment-advisor`, `team-activity-scout` and the two hooks)
predate some of these rules: they still read the team register from the project's `AGENTS.md`, list their sources in
`TEAMS.md` and stay read-only towards GitHub and Jira. [Wave 0](#planned-skills) brings them in line, with a major
version.

## Goals

1. **Generic project management.** Skills support everyday work on any project, whatever its industry, size or
   delivery approach: predictive, agile (Scrum, Kanban) or hybrid. Nothing assumes a methodology, a tool or a client.
2. **PMBOK coverage.** Together, the skills cover the seven performance domains of the PMBOK Guide, Eighth Edition
   (Governance, Scope, Schedule, Finance, Stakeholders, Resources, Risk) and the tools and techniques they use. The
   [coverage map](#coverage-map) shows what exists, what is planned and where the gaps are.
3. **Simple and minimal.** A skill states only what the model would not do by itself and leaves project management
   knowledge to the model in use.
4. **Support agents on the right model.** Work that pays off in its own context goes to an agent whose model fits
   that work.

## Principles

### A skill is a job the project manager asks for

The unit of a skill is an artifact or a recurring activity, named the way users ask for it: `risk-register`,
`status-report`, `change-request`. A skill may span several PMBOK processes. There is no skill per process (forty
triggers, far from how people talk) and no skill per domain (seven oversized skills).

Agile practices are jobs too (`sprint-planning`, `retrospective`, `flow-metrics`), tailored through the
[project register](#project-register); there is no family of skills per framework and no separate agile plugin.

Domains classify skills in the README and the manifest keywords only, never in skill names. Names are specific enough
to stay clear next to other plugins (`team-register`, not `register`). A skill name is a public contract: renaming
one is a major version.

### Write only what the model would not do by itself

The model already knows project management: the PMBOK principles and domains, the techniques, the usual documents. A
skill holds only:

- the registers and document formats it reads and writes, by reference to `shared/`;
- the capabilities and data it needs from the project's tools;
- the guardrails: writes only through declared tools, no sensitive personal data, show before writing;
- the points where the user decides;
- the shape of the output.

No project management theory, no definitions, no step-by-step instructions where judgment is enough. How much a skill
prescribes grows with the cost of an error: persistent data and writes get exact rules, drafting and analysis get
the intent. `SKILL.md` stays under about 120 lines; detail goes to `references/`, read only when needed.

### The model reasons, scripts compute

Tools and techniques live in the skills that use them: the skill names the technique and when it applies ("three-point
estimates when the user gives ranges"), and the model knows how to apply it. There is no skill per technique and no
technique catalog.

Numbers that matter (earned value, critical path, PERT, Monte Carlo, flow metrics, date arithmetic over a working
calendar) come from Python standard library scripts in `shared/scripts/`, with unit tests, never from the model's
own arithmetic.

### Skills name capabilities, not tools

Skills do not depend on any external system. A skill names the capability and the data it needs ("the transition
history of the board's issues over the last six sprints"), never a command. The systems a project uses (Jira, GitHub,
a spreadsheet, a document template) are declared in its [tools register](#tools-register), reached through an MCP
server, a CLI, a file, a skill or a script, and the model picks the right one and uses it with its own abilities and
the tool's.

Only the known pitfalls of a specific tool go in a skill's `references/`, one file per tool. Spreadsheets and other
office files are `file:` tools, read with the session's document conversion. With no tools register, a skill
suggests `/pm-skills:project-setup` and names the sources it could not read.

### Say what was read, what was inferred and what was unavailable

Every skill and agent names the sources it could not read, keeps the facts it read apart from what it inferred, and
never fills a gap with a guess.

### The user decides; the plugin proposes and acts on agreement

- **Writes go through declared tools**: a skill writes to an external system (comments, assignments, transitions,
  edits, published files) only through a tool declared with `Mode: write` in the tools register. Each write is shown
  first and made only after the user agrees; a bulk operation is confirmed on the itemized list. Collectors never
  write.
- **Show before writing**: every write in the user's project is shown first and made only after the user agrees.
- **Suggestions carry their reasons**: a skill that ranks people does it to assign work, never to appraise.

### People: delivery facts, never sensitive data or evaluations

Project files live in a repository that others read. They never hold sensitive personal data (health, reasons for an
absence, contacts beyond work accounts, individual cost) or evaluations (judgments, appraisals, personal notes).

They may hold what the project needs to plan and deliver: availability by period with no reason given, the project
calendar ("unavailable"), and delivery performance as measurable facts, by team and by person. Performance metrics
are computed when needed, never stored; rates are per role. Validators reject anything outside the schema.

### No session model assumed

Skills run on whatever model the session uses; Opus and Sonnet both have to work. Where a lighter model may lack the
knowledge, the skill names what matters instead of presuming it: for example the focus areas, by name.

### Skills compose through shared state, not calls

A skill never invokes another skill. Skills share registers and agents, and may suggest another skill to the user
("set up the project first: `/pm-skills:project-setup`"). Artifacts (visual, interactive pages for project managers)
are built in the sibling `pm-artifacts` repository and plugin; see [Publishing and artifacts](#publishing-and-artifacts).
A skill may suggest one, never depend on it.

## Patterns

### Skill anatomy

- **Frontmatter**: `name` equal to the directory; `description` under about 400 characters, saying what the skill
  does and when to use it, with specific trigger phrases in English and Italian.
- **User-invocable only**: a skill the user starts on purpose, and that would only crowd the context otherwise, sets
  `disable-model-invocation: true`: `pm-coach`, `project-setup` and `project-skill-advisor`.
- **Body**: the purpose in two lines, then **Inputs** (including the registers, project register keys and tool
  capabilities it uses), **Steps**, and **Always** / **Never**.
- **Language**: `SKILL.md` is written in English; the skill talks to the user and writes documents in the user's
  language, or in the project's `Deliverable language`.
- **README.md** next to `SKILL.md`, as `DoD.md` requires.

### Project register

Each project keeps its configuration in one register, `PROJECT.md`, and its `AGENTS.md` (or `CLAUDE.md`) declares
only that register:

```markdown
- Project register: `PROJECT.md`
```

`PROJECT.md` has four sections; the exact format will live in `shared/registers/project.md`.

| Section | What it holds |
|---|---|
| Identity | `Client`, `Project name`, `Internal code`, `Client code`, `Start date`, `Planned end date`, `Contract type` (`fixed price`, `time and materials` or `internal`), `Deliverable language` |
| Profile | the keys that tailor skills to the project (table below) |
| Conventions | document naming and versioning (see [Document naming and versioning](#document-naming-and-versioning)) |
| Registers | one line per register in use: `` - Team register: `TEAMS.md` ``, `` - Tools register: `TOOLS.md` `` |

| Profile key | Values | Used by |
|---|---|---|
| `Delivery approach` | `predictive`, `agile` or `hybrid` | tailoring in every skill |
| `Reporting cadence` | `weekly`, `biweekly`, `monthly` or free text | `status-report` |
| `Agile framework` | `scrum`, `kanban` or free text | agile skills (planned) |
| `Sprint length` | a number of weeks | Scrum skills (planned) |

`project-setup` owns `PROJECT.md` and `TOOLS.md`: it builds them over one or more sessions, section by section, and
reviews them when the project changes. Another skill that needs a missing key asks once for the session and suggests
`project-setup`. A new key or field is added to these tables by the pull request of the first skill that uses it.

### Tools register

`TOOLS.md` lists the tools the project uses and what each may do. Its format will live in
`shared/registers/tools.md`, with a validator like every register.

| Tool | Purpose | Access | Scope | Mode |
|---|---|---|---|---|
| Jira | issues | `mcp:atlassian` | project ACME | write |
| GitHub | code | `cli:gh` | acme/portal | read |
| Plan | schedule | `file:plan/acme-schedule.xlsx` | baseline and actuals | read |
| Word | publish | `skill:acme-docx` | status-report → docx | write |

- **Purpose** is a capability from a fixed vocabulary in the register's format (such as `issues`, `code`,
  `schedule`, `costs`, `publish`); skills ask for capabilities, never for a tool by name.
- **Access** says how the tool is reached: `mcp:`, `cli:`, `file:`, `skill:`, `script:` or `artifact:`.
- **Scope** says what the tool covers: a Jira project, a repository, a file's content, or, for `publish`, the
  document type and the format it produces.
- **Mode** is `read` or `write`; a skill writes only through a `write` tool, and only after the user agrees.

### Registers and documents

A **register** keeps state that persists and that another skill or a later session reads again: project, tools,
team, capacity, risks, stakeholders, decisions, changes. There is one register per type, each with its own schema;
a mixed register (a single RAID log) is not used. Every register has:

- its format in `shared/registers/<register>.md`, the single source: skills and agents point to it as
  `${CLAUDE_PLUGIN_ROOT}/shared/...` and never restate it. Headings and column names are schema keys and stay in
  English;
- its validator in `shared/scripts/`, with unit tests;
- one line in the Registers section of `PROJECT.md`.

A **document** is a snapshot: a status report, meeting minutes, a charter, lessons learned. Its format lives in
`shared/documents/<type>.md`, the single source: a common frontmatter (`type`, `project`, `date`, `version`,
`status`, `language`) and fixed headings for the type. A document has no validator and no hook. It is written where
the project's Working documents section places it, named by the project's conventions; with no such section, the
skill asks.

Deliverables are Markdown. Word, PDF, slides and artifacts are distribution formats, generated from the Markdown only
when it has to be shared or published, and generated again rather than edited.

### Document naming and versioning

Projects are under git, which keeps the history of every document. `project-setup` checks for it and proposes
`git init` when it is missing.

The Conventions section of `PROJECT.md` picks one of two naming presets at setup:

| Preset | Pattern | Example | Fits |
|---|---|---|---|
| By date | `<type>/<date>-<type>[-<slug>].md` | `status-report/2026-11-24-status-report.md` | internal projects |
| Coded | `<PROJ>-<CODE>-<NNN>[-<slug>].md` | `ACME-SR-007.md` | projects with an external client |

Type codes have defaults in the plugin and can be redefined in the project (an Italian project may use `SAL` for its
status reports). The number `NNN` is per type.

The version is always in the frontmatter (`version: 1.2.0`), and the versioning policy declared in Conventions is
always followed: major for a change of content or structure, minor for compatible extensions and clarifications,
patch for form and formatting. The version in the file name is an option, off by default, that only helps the reader:
when it is on, the name ends in the version (`ACME-SR-007-1.2.0.md`) and a `+N` suffix avoids a collision. A
distribution format keeps the base name of its Markdown source.

### Publishing and artifacts

A deliverable becomes Word, PDF, an email or an artifact only when the user asks to share or publish it. The
renderers are tools in `TOOLS.md` with `Purpose: publish`: a skill, a script, a CLI or an artifact, whose scope maps
a document type to a format. `publish-deliverable` picks the renderer for the type and format; when none is declared,
it proposes one to reuse (see [Project skills](#project-skills)) and offers to add it to the register. Its output
goes where the project's Working documents section says.

No artifact code lives in this repository. Artifacts are built in `pm-artifacts`, which holds their backlog, their
models and the skills that turn the plugin's Markdown and registers into those models. Here an artifact is only a
renderer, `artifact:<type>`.

### Project skills

A project sometimes needs a skill of its own: a Word document in the organization's format, an email, a ticketing
system with its quirks. `project-skill-advisor` helps build one only when there is a real need, after climbing the
reuse ladder:

1. a skill of this plugin;
2. a skill already available in the session, from the user or the organization (including existing templates);
3. an MCP server or a CLI;
4. a script of the project, the user or the organization;
5. a new skill in the project's `.claude/skills/`, built with `skill-creator`.

A custom skill exists to make a tool easier or safer to use, never to duplicate a pm-skills job. It follows
`shared/integration-contract.md`, which says what it reads and writes so that the plugin's skills can rely on it.
Whatever the ladder picks is recorded in `TOOLS.md`.

### Hooks

Hooks stay cheap and silent: no `UserPromptSubmit` hook, nothing printed in a project that declares no register, and
an internal error never interrupts the session. There are two: one `SessionStart` hook that sums up every declared
register in one line, and one `PostToolUse` hook (`Write`, `Edit`) that validates whichever declared register was
edited. A new register extends these two hooks; it never adds its own. Today they cover the team register only; wave
0 makes them read the registers listed in `PROJECT.md`.

### Agents

An agent exists only when its own context pays off (a lot of raw data to condense) or when work can run in
parallel; otherwise the skill does the work inline. Agents are named by function and reused across skills: check
the existing ones before adding another.

Each agent pins its model in the frontmatter by class, and says why in its body:

| Class | Model | What it does | Agents |
|---|---|---|---|
| Collector | `haiku` | gathers facts from the project's tools, read only, in a fixed output shape; no advice, no proposals | `team-activity-scout` (to become *`project-activity-scout`*), *`flow-data-scout`* |
| Analyst | `sonnet` | turns facts from several sources into an analysis or a draft | none planned |
| Critical reviewer | `opus` | challenges plans, estimates, risk responses and deliverables; finds what is missing | *`pm-critical-reviewer`* |

Names in italics are planned. Collectors feed analysts and reviewers: an agent that reasons receives the facts, it
does not gather them. A collector that reaches its tools adaptively is checked on `haiku` with its scenarios, and
moves to `sonnet` only if they fail.

### Fable escalation

No agent pins `fable`. A skill may dispatch a critical reviewer with the model overridden to `fable`, only under a
condition it writes down, such as:

- an impact analysis that spans three or more performance domains (a change touching schedule, finance and risk);
- the review of a deliverable for a steering committee or a client.

Before dispatching, the skill tells the user about the escalation and why. Fable receives facts that collectors
already prepared, and only reasons.

## Coverage map

Skills by performance domain and focus area. A skill appears in every cell it serves; planned skills are in italics.
Every pull request that adds, renames or removes a skill updates this map.

| Domain | Initiating | Planning | Executing | Monitoring and Controlling | Closing |
|---|---|---|---|---|---|
| Governance | *`project-setup`*, *`project-charter`* | | *`decision-log`* | *`status-report`*, *`change-request`*, *`decision-log`*, *`retrospective`*, *`phase-gate-review`* | *`phase-gate-review`*, *`lessons-learned`* |
| Scope | *`project-charter`* | *`wbs-builder`*, *`backlog-refinement`*, *`sprint-planning`* | | *`change-request`*, *`sprint-review`* | |
| Schedule | | *`estimate`*, *`sprint-planning`* | | *`schedule-check`*, *`flow-metrics`*, *`delivery-forecast`* | |
| Finance | | *`estimate`* | | *`budget-tracker`*, *`change-request`* | |
| Stakeholders | *`stakeholder-register`* | *`communication-plan`* | *`meeting-minutes`*, *`publish-deliverable`* | *`stakeholder-register`*, *`status-report`*, *`sprint-review`* | |
| Resources | | `team-register`, *`capacity-register`*, *`raci-matrix`* | `assignment-advisor` | `team-register`, *`capacity-register`* | |
| Risk | | *`risk-register`* | | *`risk-register`*, *`change-request`* | |

Across all domains: *`pm-coach`* and *`project-skill-advisor`*.

The focus areas come from secondary sources: the text of the guide was not available. The guide's process names and
count (forty, by the same sources) stay out of this file until someone checks them against the guide.

## Planned skills

The backlog, in waves. A wave comes before the next one because its registers are read by the skills that follow;
within a wave, skills used most often come first. Names stay provisional until a skill is published. A GitHub issue is
opened for an item only when work on it starts.

**Wave 0: foundations.** One major version.

- `project-setup` (register): builds and reviews `PROJECT.md` and `TOOLS.md` over one or more sessions; checks for
  git; shows the state of the team and suggests `team-register`. User-invocable only.
- Migration of `team-register`, `assignment-advisor` and `team-activity-scout` to `PROJECT.md`, `TOOLS.md`, adaptive
  tool use, the people rule and writes through declared tools; `team-activity-scout` becomes
  `project-activity-scout`, with a per-person and a per-project mode; the `Sources:` line of `TEAMS.md` goes away.
- `shared/documents/` with the common frontmatter and the first document formats.
- The two hooks read the registers from `PROJECT.md`.

**Wave 1: everyday work.**

| Skill | Kind | Job | Agents |
|---|---|---|---|
| `risk-register` | register | identify, assess and plan responses to risks, and review them | `pm-critical-reviewer` |
| `decision-log` | register | record decisions with their context, options and who took them | |
| `meeting-minutes` | document | minutes with decisions and actions, proposed for the decision log and the risk register | |
| `status-report` | document | the status report at the reporting cadence, from registers and tools, outcomes before activities | `project-activity-scout`, `pm-critical-reviewer` |
| `publish-deliverable` | publishing | render a Markdown deliverable in a distribution format, only on request | |
| `pm-coach` | guidance | help the project manager do the right thing with the right tools and mindset; adaptive (a few questions, then reasoned advice; "just tell me" or "let me think it through"); reads, never writes, dispatches no agent, suggests skills; user-invocable only | |

Agent: `pm-critical-reviewer` (critical reviewer, `opus`, with the Fable escalation).

**Wave 2: governance and agile.**

| Skill | Kind | Job | Agents |
|---|---|---|---|
| `change-request` | register | a change request with its impact on scope, schedule, finance and risk | `pm-critical-reviewer` |
| `stakeholder-register` | register | stakeholders, their interest, influence and engagement | |
| `capacity-register` | register | availability by period and the project calendar, with no reasons | |
| `sprint-planning` | document | sprint goal and selection against capacity | |
| `sprint-review` | document | what was delivered against the goal, and the stakeholders' feedback | |
| `retrospective` | document | what to keep, change and try, with owned actions | |
| `backlog-refinement` | analysis | readiness, splitting and ordering of backlog items | |
| `project-skill-advisor` | guidance | the reuse ladder and, for a real need, a project skill that follows the integration contract; user-invocable only | |

**Wave 3: numbers.**

| Skill | Kind | Job | Agents |
|---|---|---|---|
| `flow-metrics` | analysis | cycle time, throughput, work in progress and aging from the transition history | `flow-data-scout` |
| `delivery-forecast` | analysis | Monte Carlo forecast of dates or scope from throughput | `flow-data-scout` |
| `estimate` | analysis | three-point and analogous estimates of effort and cost | `pm-critical-reviewer` |
| `schedule-check` | analysis | critical path, float and dates over the working calendar against the baseline | |
| `budget-tracker` | analysis | spend against budget and earned value, with rates per role | |

Agent: `flow-data-scout` (collector, `haiku`): the transition history as a dataset for the scripts.

**Wave 4: life cycle.**

| Skill | Kind | Job | Agents |
|---|---|---|---|
| `project-charter` | document | purpose, objectives, scope, constraints and authority of the project | `pm-critical-reviewer` |
| `lessons-learned` | document | what the project learned, for the next one | |
| `wbs-builder` | document | the work breakdown structure and its dictionary | |
| `communication-plan` | document | who receives what, when and through which channel | |
| `raci-matrix` | document | responsibilities by deliverable or activity | |
| `phase-gate-review` | document | readiness to pass a gate or close, against its criteria | `pm-critical-reviewer` |

## PMBOK knowledge check

On 2026-11-24, closed-book tests of Opus and Sonnet named all six PMBOK 8 principles and explained them consistently
with four agreeing secondary sources, so skills do not restate them. Sonnet did not know the focus areas. Repeat the
test when the model of reference changes or PMI revises the guide.
