# Design guidelines

The goals, principles and patterns behind every skill, agent and hook of `pm-skills`. Read this file before adding
or changing one. `AGENTS.md` holds the operational rules (layout, confidentiality, version, verification); this file
says what to build and why. A rule lives in one of the two files, never in both.

## Goals

1. **Generic project management.** Skills support everyday work on any project, whatever its industry, size or
   delivery approach. Nothing assumes a methodology, a tool or a client.
2. **PMBOK coverage.** Together, the skills cover the seven performance domains of the PMBOK Guide, Eighth Edition
   (Governance, Scope, Schedule, Finance, Stakeholders, Resources, Risk) and the tools and techniques they use. The
   [coverage map](#coverage-map) shows what exists and where the gaps are.
3. **Simple and minimal.** A skill states only what the model would not do by itself and leaves project management
   knowledge to the model in use.
4. **Support agents on the right model.** Work that pays off in its own context goes to an agent whose model fits
   that work.

## Principles

### A skill is a job the project manager asks for

The unit of a skill is an artifact or a recurring activity, named the way users ask for it: `risk-register`,
`status-report`, `change-request`. A skill may span several PMBOK processes. There is no skill per process (forty
triggers, far from how people talk) and no skill per domain (seven oversized skills).

Domains classify skills in the README and the manifest keywords only, never in skill names. Names are specific enough
to stay clear next to other plugins (`team-register`, not `register`). A skill name is a public contract: renaming
one is a major version.

### Write only what the model would not do by itself

The model already knows project management: the PMBOK principles and domains, the techniques, the usual documents. A
skill holds only:

- the registers and formats it reads and writes, by reference to `shared/`;
- the sources to read, and how to read them;
- the guardrails: read-only integrations, no human resources data, show before writing;
- the points where the user decides;
- the shape of the output.

No project management theory, no definitions, no step-by-step instructions where judgment is enough. How much a skill
prescribes grows with the cost of an error: persistent data and writes get exact rules, drafting and analysis get
the intent. `SKILL.md` stays under about 120 lines; detail goes to `references/`, read only when needed.

### The model reasons, scripts compute

Tools and techniques live in the skills that use them: the skill names the technique and when it applies ("three-point
estimates when the user gives ranges"), and the model knows how to apply it. There is no skill per technique and no
technique catalog.

Numbers that matter (earned value, critical path, PERT, Monte Carlo, date arithmetic over a working calendar) come
from Python standard library scripts in `shared/scripts/`, with unit tests, never from the model's own arithmetic.

### Say what was read, what was inferred and what was unavailable

Every skill and agent names the sources it could not read, keeps the facts it read apart from what it inferred, and
never fills a gap with a guess. No integration is required: GitHub (`gh`), Jira (Atlassian MCP server or `acli`) and
the like are detected at runtime.

### The user decides; the plugin reads and proposes

- **Read-only towards GitHub and Jira**: skills and agents never comment, assign, transition or edit anything there.
  When an action is needed, they give the user the exact command.
- **Show before writing**: every write in the user's project is shown first and made only after the user agrees.
- **Project data only**: no register holds anything of human resources management (contacts, allocation,
  availability, appraisals, personal notes), and validators reject anything outside the schema.
- **Suggestions carry their reasons**: a skill that ranks people does it to assign work, never to appraise.

### No session model assumed

Skills run on whatever model the session uses; Opus and Sonnet both have to work. Where a lighter model may lack the
knowledge, the skill names what matters instead of presuming it: for example the focus areas, by name.

### Skills compose through shared state, not calls

A skill never invokes another skill. Skills share registers and agents, and may suggest another skill to the user
("set up the team register first: `/pm-skills:team-register`"). Visual pages for project managers belong to the
sibling `pm-artifacts` plugin: a skill may suggest it when it is installed, never depend on it.

## Patterns

### Skill anatomy

- **Frontmatter**: `name` equal to the directory; `description` saying what the skill does and when to use it, with
  trigger phrases in English and Italian.
- **Body**: the purpose in two lines, then **Inputs** (including the registers and profile lines it reads),
  **Steps**, and **Always** / **Never**.
- **Language**: `SKILL.md` is written in English; the skill talks to the user and writes documents in the user's
  language.
- **README.md** next to `SKILL.md`, as `DoD.md` requires.

### Registers and documents

A **register** keeps state that persists and that another skill or a later session reads again: team, risks,
stakeholders, decisions, changes. Every register has:

- its format in `shared/registers/<register>.md`, the single source: skills and agents point to it as
  `${CLAUDE_PLUGIN_ROOT}/shared/...` and never restate it. Headings and column names are schema keys and stay in
  English;
- its validator in `shared/scripts/`, with unit tests;
- one declaration line in the project's `AGENTS.md` (or `CLAUDE.md`):

  ```markdown
  - Team register: `TEAMS.md`
  ```

A **document** is a snapshot: a status report, meeting minutes, a charter, lessons learned. It has no validator and no
hook, and it is written where the project's Working documents section places it; with no such section, the skill asks.

### Project profile

A skill that adapts to the project (tailoring) reads a few declaration lines from the project's `AGENTS.md`, in the
same form as the registers:

```markdown
- Delivery approach: hybrid
- Reporting cadence: weekly
```

| Key | Values |
|---|---|
| `Delivery approach` | `predictive`, `agile` or `hybrid` |
| `Reporting cadence` | `weekly`, `biweekly`, `monthly` or free text |

A skill that needs a missing line proposes to add it (show before writing), or asks once for the session. A new key
is added to this table by the pull request of the first skill that needs it. Beyond four or five keys, the profile
becomes a register.

### Hooks

Hooks stay cheap and silent: no `UserPromptSubmit` hook, nothing printed in a project that declares no register, and
an internal error never interrupts the session. There are two: one `SessionStart` hook that sums up every declared
register in one line, and one `PostToolUse` hook (`Write`, `Edit`) that validates whichever declared register was
edited. A new register extends these two hooks; it never adds its own. Today they cover the team register only.

### Agents

An agent exists only when its own context pays off (a lot of raw data to condense) or when work can run in
parallel; otherwise the skill does the work inline. Agents are named by function and reused across skills: check
the existing ones before adding another.

Each agent pins its model in the frontmatter by class, and says why in its body:

| Class | Model | What it does | Example |
|---|---|---|---|
| Collector | `haiku` | gathers facts from sources, read only, in a fixed output shape; no advice, no proposals | `team-activity-scout` |
| Analyst | `sonnet` | turns facts from several sources into an analysis or a draft | |
| Critical reviewer | `opus` | challenges plans, estimates, risk responses and deliverables; finds what is missing | |

Collectors feed analysts and reviewers: an agent that reasons receives the facts, it does not gather them.

### Fable escalation

No agent pins `fable`. A skill may dispatch a critical reviewer with the model overridden to `fable`, only under a
condition it writes down, such as:

- an impact analysis that spans three or more performance domains (a change touching schedule, finance and risk);
- the review of a deliverable for a steering committee or a client.

Before dispatching, the skill tells the user about the escalation and why. Fable receives facts that collectors
already prepared, and only reasons.

## Coverage map

Skills by performance domain and focus area. A skill appears in every cell it serves; a planned skill is added here,
marked *planned*, once it is agreed. Every pull request that adds, renames or removes a skill updates this map.

| Domain | Initiating | Planning | Executing | Monitoring and Controlling | Closing |
|---|---|---|---|---|---|
| Governance | | | | | |
| Scope | | | | | |
| Schedule | | | | | |
| Finance | | | | | |
| Stakeholders | | | | | |
| Resources | | `team-register` | `assignment-advisor` | `team-register` | |
| Risk | | | | | |

The focus areas come from secondary sources: the text of the guide was not available. The guide's process names and
count (forty, by the same sources) stay out of this file until someone checks them against the guide.

## PMBOK knowledge check

On 2026-11-24, closed-book tests of Opus and Sonnet named all six PMBOK 8 principles and explained them consistently
with four agreeing secondary sources, so skills do not restate them. Sonnet did not know the focus areas. Repeat the
test when the model of reference changes or PMI revises the guide.
