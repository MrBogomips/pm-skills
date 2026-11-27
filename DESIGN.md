# Design guidelines

The goals, principles and patterns behind every skill, agent and hook of `pm-skills`. Read this file before adding
or changing one. `AGENTS.md` holds the operational rules (layout, confidentiality, version, verification); this file
says what to build and why. A rule lives in one of the two files, never in both.

## Goals

1. **Generic project management, optimized for software.** Skills support everyday work on any project, whatever
   its industry, size or delivery approach: predictive, agile (Scrum, Kanban) or hybrid. Nothing assumes a
   methodology, a tool or a client. They are optimized for building software and managing software products: the
   capability vocabulary includes code, CI, releases and incidents, flow metrics include the DORA metrics when the
   tools allow, risks and estimates weigh technical debt, dependencies and releases, and examples describe a software
   product. No skill requires a code tool, so a project with no software still works.
2. **PMBOK, Scrum and Kanban coverage.** Together, the skills cover the seven performance domains of the PMBOK
   Guide, Eighth Edition (Governance, Scope, Schedule, Finance, Stakeholders, Resources, Risk) and the tools and
   techniques they use. Agile skills follow the Scrum Guide (2020 edition) and the Kanban Guide (ProKanban, v2025.5);
   the Scrum Guide Expansion Pack is not a reference. The [coverage maps](#coverage-map) show what exists, what is
   planned and where the gaps are.
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
Skills serve whoever does the project management work, whatever their Scrum accountability (Product Owner, Scrum
Master, or a project manager in a hybrid project), and never give the project manager a Scrum accountability.
Scrum skills use the Scrum Guide's terms (accountabilities, events, artifacts and their commitments) without
restating the guide.

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

Only the known pitfalls of a specific tool are written down, one file per tool, in `shared/tools/<tool>.md` when
several skills or agents reach it, else in the skill's `references/`. Spreadsheets and other
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
are computed when needed, never stored; rates are per role. Flow snapshots keep work items and their
transitions, never who worked on them, so that team metrics can be recomputed and compared over time. Validators reject anything outside the schema.

### No session model assumed

Skills run on whatever model the session uses; Opus and Sonnet both have to work. Where a lighter model may lack the
knowledge, the skill names what matters instead of presuming it: for example the focus areas, by name.

### Skills compose through shared state, not calls

A skill never invokes another skill, with one exception: the handoff to the keeper of a register (below). Skills share
registers and agents, and may suggest another skill to the user ("set up the project first:
`/pm-skills:project-setup`"). Artifacts (visual, interactive pages for project managers)
are built in the sibling `pm-artifacts` repository and plugin; see [Publishing and artifacts](#publishing-and-artifacts).
A skill may suggest one, never depend on it.

### One register, one keeper

Every register has exactly one keeper skill, named on the `Kept by:` line of its format. Only the keeper writes the
register. Any other skill that finds something a register should hold (a decision taken in a meeting, a risk in a
charter, a change request in a transcript, a follow-up for the project manager) prepares a handoff proposal and, on
the user's agreement, runs the keeper with it; the keeper checks the proposal against its own rules, computes the IDs,
shows the change, writes and validates. `shared/handoff.md` holds the proposal format, the flow and the table of
keepers. The routing is exact: a proposal goes to the keeper of that register and to no other skill, and
`tests/validate.sh` checks that only the keeper's `SKILL.md` runs its register's validator. The one exception: a
keeper adds the line that declares its own register in `PROJECT.md`.

## Patterns

### Skill anatomy

- **Frontmatter**: `name` equal to the directory; `description` of at most 400 characters (the validator checks it), saying what the skill
  does and when to use it, with specific trigger phrases in English only.
- **Options**: a skill that takes options declares them in the frontmatter with `argument-hint`, since the plugin is
  Claude Code-only; the user passes them as arguments or in words, and the body says what the skill does when none is
  given. Applied to `actionable-message` first; the other skills follow (issue #29).
- **User-invocable only**: a skill the user starts on purpose, and that would only crowd the context otherwise, sets
  `disable-model-invocation: true`: `pm-coach`, `project-setup` and `pm-tailoring`.
- **Body**: the purpose in two lines, the **Italian.** line (see Glossary below), then **Inputs** (including the registers, project register keys and tool
  capabilities it uses), **Steps**, **Always** / **Never**, and **Extension points** (see
  [Tailoring](#tailoring)).
- **Language**: skills are general purpose. Frontmatter, `SKILL.md`, README and examples are in English, with the
  terms English-speaking practitioners use (a "highlight report", not a local name for it). The skill talks to the
  user and writes documents in the user's language, or in the project's `Deliverable language`.
- **Glossary**: `shared/glossary/<language>.md` maps the plugin's English terms to another language and back, one
  table per area (`it.md` for Italian). Every skill has an **Italian.** line right after its purpose: when the user
  writes in Italian or the `Deliverable language` is Italian, read the glossary first. A pointer among the Inputs is
  not enough: headless runs skipped it. The skill reads the user's words with the glossary and uses its first term
  in what it writes, the same one every time; a term marked *kept in English* is not translated. The project's
  `terms` (see [Tailoring](#tailoring)) come first. A skill is chosen from its English description, before any file
  is read: the glossary helps a skill that runs, not its triggering. A new term a skill uses in Italian goes into the
  glossary in the same pull request.
- **README.md** next to `SKILL.md`, as `DoD.md` requires.

### Project register

Each project keeps its configuration in one register, `PROJECT.md`, and its `AGENTS.md` (or `CLAUDE.md`) declares
only that register:

```markdown
- Project register: `PROJECT.md`
```

`PROJECT.md` has four sections; the exact format lives in `shared/registers/project.md`.

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
| `Agile framework` | `scrum`, `kanban` or free text | `sprint-planning`, `sprint-review`, `retrospective`, `backlog-refinement` |
| `Sprint length` | a number of weeks | `sprint-planning`, `sprint-review` |
| `Definition of Done` | the path of the project's Definition of Done | `sprint-planning`, `sprint-review`, `release-plan` |
| `Definition of Workflow` | the path of the Kanban Definition of Workflow | `sprint-planning` (Kanban replenishment), `flow-metrics`, `delivery-forecast` |

The Definition of Done and the Definition of Workflow are short, stable texts of the project, kept by
`project-setup`, with no validator. A skill that uses the Definition of Workflow names the elements it needs (work
items, start and finish points, states, WIP limits, pull policies, the Service Level Expectation) instead of
presuming them, and falls back to the board's configuration when the file is missing.

`project-setup` owns `PROJECT.md` and `TOOLS.md`: it builds them over one or more sessions, section by section, and
reviews them when the project changes. Another skill that needs a missing key asks once for the session and suggests
`project-setup`. A new key or field is added to these tables by the pull request of the first skill that uses it.

### Tools register

`TOOLS.md` lists the tools the project uses and what each may do. Its format lives in
`shared/registers/tools.md`, with a validator like every register.

| Tool | Purpose | Access | Scope | Mode |
|---|---|---|---|---|
| Jira | issues | `mcp:atlassian` | project ACME | write |
| GitHub | code | `cli:gh` | acme/portal | read |
| Plan | schedule | `file:plan/acme-schedule.xlsx` | baseline and actuals | read |
| Word | publish | `skill:acme-docx` | status-report → docx | write |

- **Purpose** is a capability from a fixed vocabulary in the register's format (such as `issues`, `code`, `ci`,
  `releases`, `incidents`, `schedule`, `costs`, `publish`); skills ask for capabilities, never for a tool by name.
- **Access** says how the tool is reached: `mcp:`, `cli:`, `file:`, `skill:`, `script:` or `artifact:`.
- **Scope** says what the tool covers: a Jira project, a repository, a file's content, or, for `publish`, the
  document type and the format it produces.
- **Mode** is `read` or `write`; a skill writes only through a `write` tool, and only after the user agrees.

### Registers and documents

A **register** keeps state that persists and that another skill or a later session reads again: project, tools,
tailoring, team, capacity, risks, stakeholders, decisions, changes, schedule, budget, RACI, gates, actions. There is one register per type, each with its own schema;
a mixed register (a single RAID log) is not used. Every register has:

- its format in `shared/registers/<register>.md`, the single source: skills and agents point to it as
  `${CLAUDE_PLUGIN_ROOT}/shared/...` and never restate it. Headings and column names are schema keys and stay in
  English;
- its keeper, on the `Kept by:` line of the format (see [One register, one keeper](#one-register-one-keeper));
- its validator in `shared/scripts/`, with unit tests;
- one line in the Registers section of `PROJECT.md`.

**One home per action.** Something to do lives in one place only. The action log (`ACTIONS.md`) holds the actions
that have no other home: actions from meetings, follow-ups, next steps a skill recommends to the project manager,
requests received. What already has a date and an owner elsewhere is not copied there: risk and stakeholder
reviews, change requests to assess or implement, gate dates and conditions stay in their registers, delivery work in
the issues tool or the schedule, retrospective actions in the retrospective. The project manager's backlog is a view
that `action-log` computes from all of them; an action turned into a work item keeps the tool and the item key, and
the tool holds its state.

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
it proposes one to reuse (see [Tailoring](#tailoring)) and offers to add it to the register. Its output
goes where the project's Working documents section says.

No artifact code lives in this repository. Artifacts are built in `pm-artifacts`, which holds their backlog, their
models and the skills that turn the plugin's Markdown and registers into those models. Here an artifact is only a
renderer, `artifact:<type>`.

### Tailoring

A project adapts the plugin to its own way of working: a risk scale from 1 to 5, a sponsor's approval above a
threshold for change requests, a section its client wants in every status report, "highlight report" instead of "status report".
`pm-tailoring` guides the user to the lightest change that does it, along a ladder:

1. a key in the Profile of `PROJECT.md`;
2. a rule on an extension point of a skill, in `TAILORING.md`;
3. a project format for a document type;
4. a tool or a renderer in `TOOLS.md`;
5. a project skill (below).

**Extension points.** Each skill lists, in its **Extension points** section, where a project may change its behavior,
using a fixed vocabulary:

| Point | What a project may change |
|---|---|
| `format` | the headings or the template of the document the skill writes |
| `scale` | scoring scales and thresholds |
| `rules` | extra checks or approvals |
| `steps` | extra steps at the named points the skill offers (for example before drafting, before writing) |
| `terms` | the project's vocabulary |

**`TAILORING.md`** is a register, declared in the Registers section of `PROJECT.md`, with one section per skill and
one entry per extension point the skill declares. Its validator rejects a skill or an extension point that does not
exist, and the two hooks cover it like every register. A skill reads its own section at the start. No rule may
loosen a guardrail: the people rule, writes through declared tools with confirmation, showing before writing and
naming the sources not read always apply. Rules can also be written by hand.

**Project skills.** A project sometimes needs a skill of its own: a Word document in the organization's format, an
email, a ticketing system with its quirks. `pm-tailoring` helps build one only for a real need, after the reuse
ladder:

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
edited. A new register extends these two hooks (its validator joins `shared/scripts/registers.py`); it never adds its
own. They read the project register from the instruction file and every register it lists.

### Agents

An agent exists only when its own context pays off (a lot of raw data to condense) or when work can run in
parallel; otherwise the skill does the work inline. Agents are named by function and reused across skills: check
the existing ones before adding another.

Each agent pins its model in the frontmatter by class, and says why in its body:

| Class | Model | What it does | Agents |
|---|---|---|---|
| Collector | `haiku` | gathers facts from the project's tools, read only, in a fixed output shape; no advice, no proposals | `project-activity-scout`, `flow-data-scout` |
| Analyst | `sonnet` | turns facts from several sources into an analysis or a draft | `register-reviewer` |
| Critical reviewer | `opus` | challenges plans, estimates, risk responses, gate assessments and deliverables; finds what is missing | `pm-critical-reviewer` |

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

Skills by performance domain and focus area. A skill appears in every cell it serves; planned skills, when
any, are in italics.
Every pull request that adds, renames or removes a skill updates this map.

| Domain | Initiating | Planning | Executing | Monitoring and Controlling | Closing |
|---|---|---|---|---|---|
| Governance | `project-setup`, `project-charter` | `product-roadmap` | `decision-log`, `action-log`, `inbox-triage` | `status-report`, `change-request`, `decision-log`, `action-log`, `retrospective`, `phase-gate-review` | `phase-gate-review`, `lessons-learned` |
| Scope | `project-charter` | `product-roadmap`, `wbs-builder`, `backlog-refinement`, `sprint-planning`, `release-plan` | | `change-request`, `sprint-review` | |
| Schedule | | `estimate`, `sprint-planning`, `release-plan` | | `schedule-check`, `flow-metrics`, `delivery-forecast` | |
| Finance | | `estimate` | | `budget-tracker`, `change-request` | |
| Stakeholders | `stakeholder-register` | `communication-plan` | `meeting-prep`, `meeting-minutes`, `publish-deliverable`, `actionable-message` | `stakeholder-register`, `status-report`, `sprint-review` | |
| Resources | | `team-register`, `capacity-register`, `raci-matrix`, `team-charter` | `assignment-advisor` | `team-register`, `capacity-register` | |
| Risk | | `risk-register` | | `risk-register`, `change-request` | |

Across all domains: `pm-coach` and `pm-tailoring`.

The focus areas come from secondary sources: the text of the guide was not available. The guide's process names and
count (forty, by the same sources) stay out of this file until someone checks them against the guide.

Scrum (Scrum Guide 2020) and Kanban (Kanban Guide v2025.5), by event, artifact and practice:

| Scrum | Skills |
|---|---|
| Sprint Planning; Sprint Backlog and Sprint Goal | `sprint-planning` |
| Daily Scrum | excluded on purpose: the Developers' event, not project management work |
| Sprint Review | `sprint-review` |
| Sprint Retrospective | `retrospective` |
| Product Backlog and Product Goal | `backlog-refinement`, `product-roadmap` |
| Increment and Definition of Done | the `Definition of Done` file in the Profile, read by `sprint-planning`, `sprint-review`, `release-plan` |

| Kanban | Skills |
|---|---|
| Defining and visualizing the workflow | the `Definition of Workflow` file in the Profile, kept by `project-setup` |
| Actively managing items in the workflow | `flow-metrics` (work item age against the Service Level Expectation) |
| Improving the workflow | `flow-metrics`, `retrospective` |
| Flow measures: WIP, throughput, work item age, cycle time | `flow-metrics`, `delivery-forecast` |

## Planned skills

The backlog, in waves. A wave comes before the next one because its registers are read by the skills that follow;
within a wave, skills used most often come first. Names stay provisional until a skill is published. A GitHub issue is
opened for an item only when work on it starts.

**Waves 0 and 1: shipped in 1.0.0.** The foundations: `project-setup` with the project and tools registers, the
tailoring register and the **Extension points** section of every skill, `shared/documents/` with the common
frontmatter, naming and versioning, hooks over every register `PROJECT.md` lists, and the migration of
`team-register`, `assignment-advisor` and the activity collector, now `project-activity-scout`. And everyday work:
`risk-register`, `decision-log`, `meeting-minutes`, `status-report`, `publish-deliverable`, `pm-coach` and the
`pm-critical-reviewer` agent.

**Wave 2: shipped in 1.1.0.** Governance and agile: `change-request` with the change log, `stakeholder-register`,
`capacity-register`, `sprint-planning`, `sprint-review`, `retrospective`, `backlog-refinement`, `product-roadmap`
and `pm-tailoring`, with `shared/integration-contract.md` for project skills.

**Wave 3: shipped in 1.2.0.** Numbers: `flow-metrics`, `delivery-forecast` and `release-plan` with the
`flow-data-scout` collector and flow snapshots, `estimate`, `schedule-check` with the schedule register and its
baselines, and `budget-tracker` with the budget register.

**Wave 4: shipped in 1.3.0.** Life cycle: `project-charter`, `wbs-builder`, `raci-matrix` with the RACI matrix,
`communication-plan`, `phase-gate-review` with the gate register, `lessons-learned` and `team-charter`. The RACI matrix
and the gates are registers rather than documents: other skills read them as state, and their validators keep one
accountable role per deliverable and the history of every gate outcome.

**After wave 4: 1.4.0.** `actionable-message`: emails and chat messages whose every request names its owner, the
ask, the deadline, the references and a contact, sent only through a declared `messages` tool.

**1.5.0.** Descriptions, READMEs and examples in English only; `shared/glossary/it.md` maps the plugin's terms to
Italian and back, and every skill reads it when the user or the `Deliverable language` is Italian.

**1.6.0.** Meetings and actions, and one keeper per register. `meeting-prep` with the `meeting-brief` document and
`shared/documents/meetings.md` for what the brief and the minutes share; `meeting-minutes` reads the brief, hands
decisions, risks, change requests and actions off to their keepers and keeps internal notes that are never
published; `action-log` with the action log (`ACTIONS.md`) and the project manager's backlog; `inbox-triage` for
incoming material; the `register-reviewer` agent (#7) for consistency between registers and alignment with the
project. Every register names its keeper and `shared/handoff.md` routes changes to it; the change log accepts a
request rejected without assessment. The user guide starts in `docs/`.

**1.7.0.** Message formats. `actionable-message` drafts in a `strong` or a `friendly` format, chosen by audience and
overridden by the options `strong`, `friendly`, `+emoji` and `-formatting` or by a `format` rule in `TAILORING.md`;
emphasis and links follow fixed rules, and `shared/scripts/message_render.py` renders the approved draft: an HTML page to
copy from for an email client, plain text for a chat pasted by hand, and Slack only for sending through a declared
`messages` tool; the assistant copies to the clipboard only on request. The user guide gains `docs/messages.md`.

**Next.** The open items are GitHub issues: the second wave of team skills (#3) and persona agents for simulated
conversations (#8).

## Knowledge check

On 2026-11-24, closed-book tests of Opus and Sonnet named all six PMBOK 8 principles and explained them consistently
with four agreeing secondary sources, so skills do not restate them. Sonnet did not know the focus areas.

The same day, a closed-book test of Sonnet got the Scrum Guide 2020 right (accountabilities, events and timeboxes,
artifacts and commitments, values, pillars, changes from 2017) and the core of the Kanban Guide (practices, flow
measures, most of the Definition of Workflow). It did not know the Scrum Guide Expansion Pack or the 2025 version of
the Kanban Guide: hence the editions named in the goals and the elements named in the profile.

Repeat the tests when the model of reference changes or a guide is revised.
