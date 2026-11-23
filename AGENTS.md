# AGENTS.md

The rules for every coding agent working in this repository.

## What this repository is

`pm-skills` is one Claude Code plugin: skills, agents and hooks that support everyday project management work,
with no particular specialization. It is listed in the `mrbogomips` marketplace, which lives in its own repository
(`MrBogomips/claude-plugins`) and reads the version from `.claude-plugin/plugin.json`:
`/plugin marketplace add MrBogomips/claude-plugins`, then `/plugin install pm-skills@mrbogomips`. Skills are invoked
as `/pm-skills:<name>`.

The plugin is Claude Code-only on purpose: skills share formats and scripts through `${CLAUDE_PLUGIN_ROOT}`, and the
plugin ships agents and hooks. It is not distributed through the `skills` CLI.

Skills are grouped by the seven PMBOK 8 performance domains (Governance, Scope, Schedule, Finance, Stakeholders,
Resources, Risk) in the README and the keywords only, never in skill names. Visual pages for project managers belong
to the sibling `pm-artifacts` plugin: a skill may suggest it when it is installed, never depend on it.

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
shared/scripts/                     Python stdlib scripts shared by skills and hooks
tests/                              validate.sh, selftest.sh, Python unit tests, fixtures/, scenarios/
```

## Registers

Skills keep project state in Markdown registers inside the user's project. Each register's format is written once in
`shared/registers/` and implemented once in `shared/scripts/`; skills and agents point to them as
`${CLAUDE_PLUGIN_ROOT}/shared/...` and never restate them. A project declares a register in its `AGENTS.md` (or
`CLAUDE.md`) with one line, for example:

```markdown
- Team register: `TEAMS.md`
```

Registers hold project data only. Nothing of human resources management goes into them: no contacts, allocation,
availability, appraisals or personal notes. Validators reject anything outside the schema.

## Writing rules

- `SKILL.md` files and agents are written in English; skills talk to the user and write documents in the user's
  language. Register headings and column names are schema keys and stay in English.
- Names are specific enough to stay clear next to other plugins (`team-register`, not `register`); the frontmatter
  `name` equals the directory (skills) or the file name (agents).
- No integration is required: GitHub (`gh`), Jira (Atlassian MCP server or `acli`) and the like are detected at
  runtime, and a skill says which source was unavailable instead of guessing.
- Skills and agents read GitHub and Jira; they never write to them.
- Hooks stay cheap and silent: no `UserPromptSubmit` hook, nothing printed in projects that declare no register, and
  an internal error never interrupts the session.
- Scripts are Python 3 standard library, macOS and Linux compatible; shell scripts are bash 3.2, with no `grep -P`
  and no `sed -i`.

## Version

Every pull request that changes what the plugin does bumps `version` in `.claude-plugin/plugin.json` once: patch for
a fix, minor for a new skill, agent or hook or a compatible extension, major when a component is renamed or removed
or its behavior changes incompatibly. Claude Code updates installed plugins only when the version changes.

## Verification

From the repository root (requires `jq`):

```bash
bash tests/selftest.sh                                  # the validator's own tests
PM_SKILLS_FORBIDDEN_TERMS=<local file> bash tests/validate.sh   # plugin structure and confidentiality
python3 -m unittest discover -s tests -p 'test_*.py'    # shared scripts and hooks
claude plugin validate . --strict                       # manifest schema
```

Skills and agents are checked with the manual scenarios in `tests/scenarios/<component>/`. To try the plugin without
installing it: `claude --plugin-dir .`.

## Working documents

- **Authoritative**: `skills/`, `agents/`, `hooks/`, `shared/` and `.claude-plugin/plugin.json`.
- **AI working material** (brainstorms, plans, decision logs) stays in the session scratchpad; nothing is written to
  the repository for it. Tool defaults such as `docs/superpowers/...` follow this rule too.

## Git / PR Working Policy
- Worktree usage: disabled
- Worktree location: n/a (topic branch in main checkout)
- Base branch: main
- Recorded on: 2026-11-23
