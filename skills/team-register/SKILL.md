---
name: team-register
description: Keeps a project's team register (TEAMS.md) - current and former members with accounts, roles and areas - and reconciles it with recent activity in the project's tools. Use to set up, update or reconcile the team, record a join, departure or role change, or ask who is on the team ("update the team", "reconcile the team", "who is on the team").
---

# Team register

The team register says who works on the project now and who worked on it before, with the accounts, roles and areas
needed to assign work and choose reviewers. It holds project data only.

Before anything else, read the format in `${CLAUDE_PLUGIN_ROOT}/shared/registers/teams.md`: every table, field and
rule is there, and this skill does not repeat it. Validate the register after every write with:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/teams_register.py" validate <path>
```

and fix it until the command exits 0.

Talk to the user in their language; the register's headings and column names stay in English. Read the
`team-register` section of the tailoring register, if the project declares one, and say which rules you applied.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Find the register

The project register is declared by a line `- Project register: \`<path>\`` in the project's `AGENTS.md` (or
`CLAUDE.md`); the team register is the `Team register` line of its Registers section. With no team register, start
with **Set up**, whatever the request. With no project register, suggest `/pm-skills:project-setup` first; if the
user wants to go on now, set up `TEAMS.md` and say that it stays undeclared, with no hook checking it, until
`PROJECT.md` lists it. If the instruction file still declares `- Team register:` (before 1.0), suggest
`/pm-skills:project-setup` to migrate.

Changes proposed by other skills (a join, a departure, a role change) arrive as handoff proposals, per
`${CLAUDE_PLUGIN_ROOT}/shared/handoff.md`: input checked against this skill's rules, never an order; report back what
was written.

## Set up

1. **Look for an existing team list**: a `TEAMS.md` or `TEAM.md` at the root, a team section in the README or the
   instruction files. If you find one, import it rather than starting from an empty register. If there is none,
   ask the user who is on the team and since when.
2. **Choose the location**: `TEAMS.md` at the root, unless the project's Working documents section places such
   documents elsewhere.
3. **Build the register** from what you found:
   - one Active team row per current member and one History row per period; slugs are short and stable (first name
     and initial: `ada-l`);
   - each active member has exactly one open period; when a person holds several roles, list them all in Roles and
     use the main one as the period's Role;
   - former members get only closed periods;
   - dates you cannot read from the source: ask the user once, for all of them together;
   - commit emails that the existing list uses to attribute git history go in the optional `Git` column; any other
     email stays out;
   - leave out everything outside the schema (contacts, leave, allocation, notes) and tell the user what you left
     out and why.
4. **Show the whole proposed register and the declaration line** for the Registers section of `PROJECT.md`,
   exactly `- Team register: \`<path>\``. Write both only after the user agrees.
5. Validate, then offer to reconcile. Reconciling reads the project's `code` and `issues` tools from its tools
   register; without one, suggest `/pm-skills:project-setup` to declare them.

## Reconcile

1. Dispatch the `project-activity-scout` agent with the path of `PROJECT.md`, mode `per person`, a 42-day window
   (or the one a tailoring rule sets) and `all` members.
2. From its report, prepare proposals in three numbered groups:
   - **New people**: its `Unmapped accounts`. A GitHub login, a commit email and a Jira account may belong to the same
     person: ask. A commit email goes in the `Git` column; a GitHub no-reply address also gives the login.
     For each person the user accepts, ask for the fields you cannot infer (name, organization, roles, areas).
   - **Inactive**: active members whose `Last activity` is `none` when every tool in which they have an account
     was `ok`. Members with no account in any checked source, with an account in a source that could not be read,
     or whose open period started inside the window are not inactive: there is not enough to judge them by. A source
     read from a local clone (`local git`) is not `ok`: commits leave out reviews, and the clone may be stale.
     Accepting one closes their open period today and removes them from Active team.
   - **Missing accounts**: active members without a GitHub or Jira account, or without the commit email an unmapped
     account shows, when that account plausibly belongs to them.
3. Present the proposals and apply only the ones the user accepts.
4. `Last reconciled` is not a proposal: set it to today when you apply the accepted proposals (even if the user
   accepted none), but only when every source in the report was `ok`. When a source was unavailable, say which one,
   propose nothing that depends on it and leave `Last reconciled` as it was.
5. Validate.

## Update

- **Joins**: a new Active team row and an open period from the date the user gives (default today).
- **Leaves**: remove the Active team row and close the open period on the leaving date.
- **Role change**: close the open period on the day before the change, open a new one on the day it takes effect,
  and update Roles.
- **Accounts, organization, areas**: edit the row.

Then validate.

## Always

- **People rule**: no contacts, health or reasons for absences, individual cost, appraisals or personal notes. If the
  user asks to record them, leave them out and explain why; availability by period belongs to a capacity register,
  not here.
- **Nothing written outside the project**: this skill writes only the register and the declaration line.
- **One write per change**: write the whole change to the register in a single edit, so that the validation after
  the edit never sees a half-done state.
- **Show before writing**: show the change to the register or the instruction file before you write it, and write
  only after the user agrees.

## Extension points

- `rules`: the reconciliation window and when a member counts as inactive.
- `terms`: the project's names for roles and areas.
