# AGENTS.md

The rules for every coding agent working in this repository.

## What this repository is

`pm-skills` is one Claude Code plugin: skills, agents and hooks that support everyday project management work on
any project, optimized for software. It is listed in the `mrbogomips` marketplace, which lives in its own repository
(`MrBogomips/claude-plugins`) and reads the version from `.claude-plugin/plugin.json`:
`/plugin marketplace add MrBogomips/claude-plugins`, then `/plugin install pm-skills@mrbogomips`. Skills are invoked
as `/pm-skills:<name>`.

The plugin is Claude Code-only on purpose: skills share formats and scripts through `${CLAUDE_PLUGIN_ROOT}`, and the
plugin ships agents and hooks. It is not distributed through the `skills` CLI.

**Read `DESIGN.md` before adding or changing a skill, agent or hook.** It holds the design goals, principles and
patterns: what a skill is, what it leaves to the model, registers and documents, the project and tools registers,
hooks, agents and their models, the PMBOK, Scrum and Kanban coverage maps and the planned skills. This file holds
the operational rules only.

## Confidentiality

This repository is public. No client names, client data or client conventions in any file: examples, fixtures and
scenarios use an invented team and project (Acme). Projects where the plugin is tested stay out of the repository.

The list of forbidden terms lives outside the repository, in a local file named by `PM_SKILLS_FORBIDDEN_TERMS` (one
term per line, `#` for comments). `tests/validate.sh` checks every file against it when the variable is set, and
warns when it is not; set it before every pull request.

## Layout

```
.claude-plugin/plugin.json          the plugin manifest: no `skills` field, no marketplace.json
skills/<name>/SKILL.md              one directory per skill, with its README.md and references/ if needed
agents/<name>.md                    subagents of the plugin
hooks/hooks.json, hooks/*.py        hooks and their scripts
shared/registers/<register>.md      the format of each project register: the single source, read by skills
shared/documents/<type>.md          the format of each document type, and common.md for what they share
shared/tools/<tool>.md              known pitfalls of a tool reached by several skills or agents
shared/glossary/<language>.md       the plugin's terms in another language and back (it.md for Italian)
shared/handoff.md                   the keeper of each register and how other skills hand changes off to it
shared/integration-contract.md      what a project skill must respect to work with the plugin
shared/scripts/                     Python stdlib scripts shared by skills and hooks
tests/                              validate.sh, selftest.sh, Python unit tests, fixtures/, scenarios/
docs/                               the user guide: principles, patterns and practices of the plugin
.claude/agents/, .claude/skills/    the repository harness: not part of the plugin (below)
```

## Repository harness

Two kinds of skills and agents live in this repository, and they never mix:

- **The plugin**: `skills/`, `agents/` and `hooks/`, distributed to users. Nothing there serves the maintenance of
  this repository.
- **The harness**: `.claude/agents/` and `.claude/skills/`, which help maintain and evolve the plugin. Claude Code
  loads them in sessions opened in this repository; the plugin never loads them and users never receive them. They
  follow the writing rules below, but are not listed in `README.md`, the coverage map or the user guide.

| Harness component | What it does |
|---|---|
| `.claude/agents/user-docs-reviewer.md` | reviews the user guide in `docs/` against a pull request's changes, read only |

## User guide

`docs/` holds the user guide: the principles, patterns and practices of the plugin, for the people who use it. Each
page starts with a frontmatter that `tests/validate.sh` checks:

```yaml
---
title: Registers and their keepers
area: plugin            # plugin, or a performance domain: governance, scope, schedule, finance, stakeholders, resources, risk
type: concept           # concept (why and how it works) or operational (how to do a job)
---
```

`docs/skills.md` lists every skill of the plugin; the validator checks that none is missing. Every pull request that
adds or changes a skill, agent, hook, register or document format updates the guide in the same pull request, and
has it reviewed by the `user-docs-reviewer` agent before the pull request is opened.

## Writing rules

- Skills and agents are general purpose: frontmatter, `SKILL.md`, agents, READMEs and examples are in English, with
  terms English-speaking practitioners use; skills talk to the user and write documents in the user's language,
  with the terms of `shared/glossary/` (see `DESIGN.md`, Skill anatomy).
- The frontmatter `name` equals the directory (skills) or the file name (agents).
- Scripts are Python 3 standard library, macOS and Linux compatible; shell scripts are bash 3.2, with no `grep -P`
  and no `sed -i`.

Naming, registers, integrations, hooks and agents follow `DESIGN.md`.

## Version

Every pull request that changes what the plugin does bumps `version` in `.claude-plugin/plugin.json` once: patch for
a fix, minor for a new skill, agent or hook or a compatible extension, major when a component is renamed or removed
or its behavior changes incompatibly. Claude Code updates installed plugins only when the version changes.

## Verification

From the repository root (requires `jq`):

```bash
bash tests/selftest.sh                                  # the validator's own tests
PM_SKILLS_FORBIDDEN_TERMS=<local file> bash tests/validate.sh   # plugin structure and confidentiality
python3 -m unittest discover -s tests -p 'test_*.py'    # shared scripts and hooks (also with /usr/bin/python3)
claude plugin validate . --strict                       # manifest schema
```

Skills and agents are checked with the manual scenarios in `tests/scenarios/<component>/`. To try the plugin without
installing it: `claude --plugin-dir .`.

## Working documents

- **Authoritative**: `DESIGN.md`, `skills/`, `agents/`, `hooks/`, `shared/`, `docs/` and
  `.claude-plugin/plugin.json`.
- **AI working material** (brainstorms, plans, decision logs) stays in the session scratchpad; nothing is written to
  the repository for it. Tool defaults such as `docs/superpowers/...` follow this rule too.

## Git / PR Working Policy
- Worktree usage: disabled
- Worktree location: n/a (topic branch in main checkout)
- Base branch: main
- Recorded on: 2026-11-23
