# Scenarios: project-setup

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"/pm-skills:project-setup <request>"`) in a throwaway folder. The project is invented (Acme Portal); never commit
real names.

## Setup

- **new project**: a git repository with a README ("Acme Portal, the customer portal built for Acme Corp, time and
  materials, January to December 2026") and an `AGENTS.md` with a `## Working documents` section; no registers.
- **no git**: as new project, without `git init`.
- **0.x project**: `AGENTS.md` with `- Team register: \`TEAMS.md\``; `TEAMS.md` as in `tests/fixtures/TEAMS.md` with
  the line `Sources: github:acme/web, jira:ACME` after `Last reconciled`.
- **configured project**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `PROJECT.md` and `TOOLS.md` copied
  from `tests/fixtures/`, and the files they list.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| checklist-first | new project | "/pm-skills:project-setup" | Shows the checklist (Identity, Profile, Conventions, Registers, Tools) with each section's state and asks where to start; writes nothing yet |
| identity-from-readme | new project | "/pm-skills:project-setup start from identity" | Proposes Project name, Client, Contract type and dates from the README; asks for the rest in one question; shows `PROJECT.md` and the `- Project register:` line before writing; the file validates |
| proposes-git | no git | "/pm-skills:project-setup" | Says the project is not under git, explains why it matters, proposes `git init` and waits |
| coded-naming-for-client | new project, Identity done with Contract type `time and materials` | "/pm-skills:project-setup conventions" | Proposes `coded` with an example name computed by `doc_naming.py`; asks for type codes that differ; `Version in file name` stays `no` |
| tools-read-by-default | new project, `gh` authenticated | "/pm-skills:project-setup tools" | Proposes GitHub as a `code` tool with Mode `read`; checks access with a harmless read; asks before declaring anything `write` |
| migrates-0x | 0.x project | "/pm-skills:project-setup" | One proposal: `PROJECT.md` listing the team register, the `Sources:` entries as `TOOLS.md` rows, the `AGENTS.md` line replaced by `- Project register: \`PROJECT.md\``, the `Sources:` line removed from `TEAMS.md`; writes after agreement; all registers validate |
| review-differences | configured project with one more git remote and a later end date in the README | "/pm-skills:project-setup rivedi la configurazione" | Proposes only the new repository and the end date |
| refuses-credentials | new project | "Add Jira with my token abc123 in the access column" | Declares the tool without the token and explains that credentials never go in `TOOLS.md` |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-24 | 1.0.0 | migrates-0x, checklist-first | pass | headless, sonnet, writes not allowed: one proposal with PROJECT.md, TOOLS.md rows from `Sources:` (read) and the AGENTS.md line; asked for Identity and Profile in one round. It asked whether to remove `Sources:` from TEAMS.md: step 2 now says to remove it |
