---
name: assignment-advisor
description: Suggests who on the team should take a task or review a pull request or a document, with the reasons for each candidate - matching areas in the team register, recent activity, open load - and assigns only when the user agrees, through a tool declared for writing. Use when the user asks who should take or review something ("suggest a reviewer", "who should take this", "who should review this PR").
---

# Assignment advisor

Suggests up to three people for a piece of work, each with the reasons, from the project's team register and the
team's recent activity. The user decides; the skill assigns or requests a review only on their agreement.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **The work**: an issue key (`ACME-123`), a pull request (URL or `<owner>/<repo>#<n>`), a document path, or a short
  description of a task.
- **The registers**: the project register is declared by `- Project register: \`<path>\`` in the project's
  `AGENTS.md` (or `CLAUDE.md`); its Registers section names the team register (format in
  `${CLAUDE_PLUGIN_ROOT}/shared/registers/teams.md`) and the tools register (format in
  `${CLAUDE_PLUGIN_ROOT}/shared/registers/tools.md`). With no team register, say so and point to
  `/pm-skills:team-register`; do not guess a team from the tools. With no project register, point to
  `/pm-skills:project-setup`.
- **Capabilities**: `issues` (summary, description, components, labels and assignee of a task; open load per person)
  and `code` (author, files, reviews and review requests of a pull request), from the tools register. Known pitfalls
  of specific tools are in `${CLAUDE_PLUGIN_ROOT}/shared/tools/`.
- **Tailoring**: the `assignment-advisor` section of the tailoring register, if declared; say which rules you applied.

## Steps

1. **Understand the work.** Read only what you need, by reading: the pull request's author, title, changed files,
   reviews and review requests; the task's summary, description, components, labels and current assignee; a
   document's title and headings. From this, name the areas the work touches in the register's vocabulary.
2. **Exclude** who cannot take it: for a pull request its author and anyone who already approved it; for a task its
   current assignee. Former members are never candidates.
3. **Gather activity.** Dispatch the `project-activity-scout` agent with the path of `PROJECT.md`, mode
   `per person`, a 42-day window and the remaining members whose Areas or Roles fit the work (all remaining members
   if none fits). Always dispatch it, even when Areas alone seem to settle the choice: recent activity and open load
   are part of every answer. Wait for its report before ranking.
4. **Rank** the candidates, in this order of weight:
   1. Areas matching the areas of the work;
   2. recent activity in the repositories involved: pull requests authored and reviewed there, or commits when the
      scout could read only a local clone;
   3. lighter open load, as a tie-breaker.

   A member with no data in the scout's report keeps their place by Areas, with a note that there is no activity
   data for them.
5. **Answer** with at most three candidates, best first:

   ```markdown
   1. **<Name>** (`<slug>`): <one line on why>
      - Areas: <matching areas>
      - Activity: <for example "5 PRs authored and 12 reviewed in acme/web in the last 42 days">
      - Load: <for example "3 open issues">
   ```

   Then one line per exclusion (who and why) and one line per tool the scout could not read.
6. **Act on agreement.** If the user picks a candidate and asks to assign or request the review, do it only through a
   tool the tools register declares with `Mode: write` for that capability: show the exact change (who, what, where)
   and make it after the user confirms. With no such tool, give the exact step or command instead, for example
   `gh pr edit <n> --repo <owner>/<repo> --add-reviewer <login>`.

## Always

- Suggestions exist to assign work, never to appraise people: reasons are areas, activity and load, as facts.
- When the work itself cannot be read (no `code` or `issues` tool, or the tool is unavailable), ask the user for what
  you need (author, title, files or areas) before ranking.

## Never

- Never assign, request a review, comment or change anything in a tool without the user's explicit agreement to that
  change, or through a tool that is not declared `write`.
- Never write files: the answer lives in the conversation.
- Never invent activity: when a tool is unavailable, say so and rank on the register alone.

## Extension points

- `rules`: who may not take or review which work (for example "no self-review across suppliers"), the window, extra
  exclusions.
- `scale`: the weights of areas, activity and load, and the number of candidates.
