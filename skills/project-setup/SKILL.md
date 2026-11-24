---
name: project-setup
description: Sets up and reviews a project's configuration for pm-skills - PROJECT.md (identity, profile, conventions, registers) and TOOLS.md (the tools and what each may do) - over one or more sessions, checks for git, and migrates projects from before 1.0. Use to set up, configure, review or migrate the project ("configura il progetto", "imposta pm-skills", "rivedi la configurazione").
disable-model-invocation: true
---

# Project setup

Builds and keeps the project register (`PROJECT.md`) and the tools register (`TOOLS.md`), section by section, over
as many sessions as the user needs; reviews them when the project changes. Every other skill reads them.

## Inputs

- Formats, read before anything else and never restated: `${CLAUDE_PLUGIN_ROOT}/shared/registers/project.md` and
  `${CLAUDE_PLUGIN_ROOT}/shared/registers/tools.md`; for naming, `${CLAUDE_PLUGIN_ROOT}/shared/documents/common.md`.
- The project's `AGENTS.md` (or `CLAUDE.md` when it has no `AGENTS.md`), its Working documents section, its README,
  its git remotes, and whatever already describes the project (a charter, a contract summary, an existing team list).
- The tools the session can reach: connected MCP servers, CLIs on the `PATH`, files in the project.

## Steps

1. **Take stock.** Find the declaration `- Project register: \`<path>\`` in `AGENTS.md`, else `CLAUDE.md`, and read
   the registers it points to. Check that the project is under git (`git rev-parse --is-inside-work-tree`); if it is
   not, explain that git keeps the history of every document and register, and propose `git init`.
   Show a checklist of the sections (Identity, Profile, Conventions, Registers, Tools), each `done`, `partial` or
   `missing`, and ask where to start; by default, the first one not done. The user may stop after any section.
2. **Migrate a project from before 1.0** when `AGENTS.md` or `CLAUDE.md` still declares `- Team register:` and no
   project register: propose `PROJECT.md` with that register in its Registers section, the instruction-file line
   replaced by `- Project register: \`PROJECT.md\``, and the team register's `Sources:` line moved to `TOOLS.md` as
   rows (`github:<owner>/<repo>` → a GitHub tool with Purpose `code`, `jira:<KEY>` → a Jira tool with Purpose
   `issues`, both `read` unless the user says otherwise), and the `Sources:` line removed from the team register (the
   1.0 validator rejects it). Show all the changes together, then write them.
3. **Identity.** Propose the values you can read (project name from the README, client and codes from the documents),
   ask once for the rest, all together. `Internal code` is needed for coded document names. Leave out what the user
   does not know yet.
4. **Profile.** Ask for the delivery approach and the reporting cadence; for agile or hybrid, the framework and, for
   Scrum, the sprint length. Offer to record the paths of an existing Definition of Done and, for Kanban, Definition
   of Workflow; if the user wants one written, draft it with them as a short project file (for the Definition of
   Workflow: work items, start and finish points, states, WIP limits, pull policies, the Service Level Expectation).
5. **Conventions.** Propose `coded` when the project has an external client (`Contract type` other than `internal`),
   `by date` otherwise; show an example name for each from `doc_naming.py`. Ask for type codes that differ from the
   defaults (an Italian project may want `status-report=SAL`). The version in the file name stays `no` unless asked.
   If the instruction file has no Working documents section, propose where documents go and record it there.
6. **Tools.** Propose rows from what the session can reach and what the project mentions: MCP servers (`mcp:`), CLIs
   (`cli:`) checked with a harmless read (`gh auth status`), office files that hold plans or costs (`file:`), and
   publishing templates or skills (`skill:`, `script:`). For each: Purpose from the vocabulary, Scope (which project,
   repositories, file content, or `<type> → <format>` for publish) and Mode. Mode is `read` by default; `write` only
   when the user wants skills to write there, after you explain that each write is still shown and confirmed.
7. **Registers.** List the registers in use and the skill that keeps each. Show the state of the team: with a team
   register, its one-line summary; without, suggest `/pm-skills:team-register`. Add a register line only for a file
   that exists or that the user is about to create with its skill.
8. **Write.** Show the whole change (the new or changed sections, the instruction-file line, exactly
   `- Project register: \`PROJECT.md\`` with nothing after the path) and write only after the user agrees, in one
   edit per file. Validate:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/project_register.py" validate <PROJECT.md>
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/tools_register.py" validate <TOOLS.md>
   ```

   and fix until both exit 0. End with the checklist again and what is left for a later session.

**Review** ("rivedi la configurazione"): run the checklist, compare each section with what the project shows now
(new repositories, a tool no longer reachable, a changed end date, a register declared but missing), and propose
only the differences.

## Always

- Ask for all the missing values of a section at once, never one question per key.
- Keep `PROJECT.md` and `TOOLS.md` within their formats: no notes, no keys outside the schema; tell the user what you
  left out.
- Credentials never go in `TOOLS.md`: Access says how a tool is reached, never a token or a password.

## Never

- Never write a register, the instruction file or a Definition of Done without showing it first.
- Never declare a tool `write` on your own, and never test a tool with a write.
- Never record people's data here: the team lives in the team register.

## Extension points

None. The project register and the tools register are the configuration that tailoring builds on.
