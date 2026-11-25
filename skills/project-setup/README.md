---
summary: For project managers - sets up and reviews the project's configuration for pm-skills (PROJECT.md and TOOLS.md), one section at a time, and migrates projects from earlier versions.
---

# project-setup

Builds the two files every pm-skills skill reads: `PROJECT.md`, with who the project is for, how it is delivered,
how its documents are named and which registers it keeps; and `TOOLS.md`, with the tools the project uses and what
skills may do with each. It works section by section, over as many sessions as you need, and reviews both when the
project changes.

## Why

Skills that know the project's delivery approach, reporting cadence, naming convention and tools do the right thing
without asking every time. This skill collects that once, from what the project already shows (README, git remotes,
connected tools) and from a few grouped questions, and keeps it in two small validated files under git. It also
moves a project from the 0.x layout, where the team register was declared in `AGENTS.md`, to the 1.0 layout.

## Use cases

### Set up a new project

**Context:** A new client project, Acme Portal, with Jira and GitHub connected to the session.

**Action:** Run `/pm-skills:project-setup`.

**Result:** A checklist of sections; identity, profile and conventions proposed from the README and a few questions;
Jira and GitHub proposed as tools, read only unless you choose otherwise; `PROJECT.md`, `TOOLS.md` and the
`- Project register:` line in `AGENTS.md`, written after you see them.

### Migrate from pm-skills 0.x

**Context:** `AGENTS.md` declares `- Team register: \`TEAMS.md\`` and the register has a `Sources:` line.

**Action:** Run `/pm-skills:project-setup`.

**Result:** One proposal with `PROJECT.md` listing the team register, the sources moved to `TOOLS.md`, and the
instruction-file line replaced; nothing is written before you agree.

### Review the configuration

**Context:** The project added a repository and moved its end date.

**Action:** Run `/pm-skills:project-setup` and say "review the configuration".

**Result:** Only the differences between the registers and what the project shows now, as proposals.

## Usage

User-invocable only: run `/pm-skills:project-setup`. Stop after any section and resume in a later session.

## Inputs and outputs

- Reads `AGENTS.md` or `CLAUDE.md`, the README, git remotes, the tools the session can reach and existing registers.
- Writes `PROJECT.md`, `TOOLS.md`, the `- Project register:` line in the instruction file and, if you ask, a
  Definition of Done or of Workflow; formats in [`shared/registers/project.md`](../../shared/registers/project.md)
  and [`shared/registers/tools.md`](../../shared/registers/tools.md).

## Requirements

Python 3 for the validators; git, which the skill offers to initialize when the project lacks it.

## Limitations

- Does not keep the team: it shows its state and points to `team-register`.
- Never declares a tool writable on its own, and never tests a tool with a write.
