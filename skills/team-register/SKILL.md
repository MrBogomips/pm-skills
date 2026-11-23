---
name: team-register
description: Creates and maintains a project's team register (TEAMS.md) - who is on the team now and who was before, with GitHub and Jira accounts, roles and areas - and reconciles it with recent GitHub and Jira activity. Use when the user asks to set up, import, update or reconcile the team register or TEAMS.md, to record that someone joined, left or changed role, or asks who is on the team ("aggiorna il team", "riconcilia il team", "chi c'è nel team", "registro del team").
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

Talk to the user in their language; the register's headings and column names stay in English.

## Find the register

The project declares it with a line `- Team register: \`<path>\`` in its `AGENTS.md`, or in its `CLAUDE.md` when
`AGENTS.md` has no such line. With no such line, start with **Set up**, whatever the request.

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
4. **Propose the sources**: the GitHub repositories of the project (its git remotes, and those of repositories
   nested in it or listed in its instruction files) and the Jira project keys its instruction files mention. The user
   confirms or corrects them.
5. **Show the whole proposed register and the declaration line**, exactly `- Team register: \`<path>\``, with where
   it goes: in the Working documents section of the instruction file if there is one, otherwise at its end. Add no
   text after the path. Write both only after the user agrees.
6. Validate, then offer to reconcile.

## Reconcile

1. Dispatch the `team-activity-scout` agent with the register's path, a 42-day window and `all` members.
2. From its report, prepare proposals in three numbered groups:
   - **New people**: its `Unmapped accounts`. A GitHub login and a Jira account may belong to the same person: ask.
     For each person the user accepts, ask for the fields you cannot infer (name, organization, roles, areas).
   - **Inactive**: active members whose `Last activity` is `none` when every source in which they have an account
     was `ok`. Members with no account in any checked source, with an account in a source that could not be read,
     or whose open period started inside the window are not inactive: there is not enough to judge them by.
     Accepting one closes their open period today and removes them from Active team.
   - **Missing accounts**: active members without a GitHub or Jira account when an unmapped account plausibly
     belongs to them.
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

- **No human resources data**: if the user asks to record contacts, leave, availability, allocation, appraisals or
  personal notes, do not record them, and explain that the register holds project data only.
- **Read-only towards GitHub and Jira**: never comment, assign, transition or edit anything there.
- **One write per change**: write the whole change to the register in a single edit, so that the validation after
  the edit never sees a half-done state.
- **Show before writing**: show the change to the register or the instruction file before you write it, and write
  only after the user agrees.
