---
name: assignment-advisor
description: Suggests who on the team should take a Jira task or review a pull request or a document, with the reasons for each candidate - matching areas in the team register, recent activity in the repositories involved, open Jira load - and never assigns or requests anything itself. Use when the user asks who should take, be assigned or review something ("who should review this PR", "suggest a reviewer", "a chi assegno", "chi revisiona", "chi prende questo task").
---

# Assignment advisor

Suggests up to three people for a piece of work, each with the reasons, from the project's team register and the
team's recent activity. It suggests only: the user, or a session with that permission, makes the assignment.

## Inputs

- **The work**: a Jira key (`ACME-123`), a pull request (URL or `<owner>/<repo>#<n>`), or a document path; or a short
  description of a task.
- **The register**: declared by a line `- Team register: \`<path>\`` in the project's `AGENTS.md`, or in its
  `CLAUDE.md` when `AGENTS.md` has no such line.
  Its format is in `${CLAUDE_PLUGIN_ROOT}/shared/registers/teams.md`. With no register, say so and point to
  `/pm-skills:team-register`; do not guess a team from GitHub or Jira.

## Steps

1. **Understand the work.** Read only what you need, and only by reading commands:
   - pull request: `gh pr view <n> --repo <owner>/<repo> --json author,title,files,reviews,reviewRequests,labels`;
   - Jira task: summary, description, components, labels and current assignee, through the Atlassian MCP server or
     `acli`;
   - document: its path, title and headings.

   From this, name the areas the work touches (modules, repositories, kinds of work) in the register's vocabulary.
2. **Exclude** who cannot take it: for a pull request its author and anyone who already approved it; for a Jira task
   its current assignee. Former members are never candidates.
3. **Gather activity.** Dispatch the `team-activity-scout` agent with the register's path, a 42-day window and the
   remaining members whose Areas or Roles fit the work (all remaining members if none fits). Always dispatch it, even
   when Areas alone seem to settle the choice: recent activity and open load are part of every answer, and wait for
   its report before ranking.
4. **Rank** the candidates, in this order of weight:
   1. Areas matching the areas of the work;
   2. recent activity in the repositories involved: pull requests authored and reviewed there;
   3. lighter open Jira load, as a tie-breaker.

   A member with no data in the scout's report keeps their place by Areas, with a note that there is no activity
   data for them.
5. **Answer** with at most three candidates, best first:

   ```markdown
   1. **<Name>** (`<slug>`): <one line on why>
      - Areas: <matching areas>
      - Activity: <for example "5 PRs authored and 12 reviewed in owner/repo in the last 42 days">
      - Load: <for example "3 open Jira issues">
   ```

   Then one line per exclusion (who and why) and one line per source the scout could not read.

## Never

- Never assign an issue, request a review, comment or change anything on GitHub or Jira, even when the user asks you
  to go ahead. Give the user the exact command or step instead, for example
  `gh pr edit <n> --repo <owner>/<repo> --add-reviewer <login>`, and leave it to them or to a session that has that
  permission.
- Never write files: the answer lives in the conversation.
- Never invent activity: when a source is unavailable, say so and rank on the register alone. When the work
  itself cannot be read (a pull request without `gh`, a Jira key without Jira access), ask the user for what you
  need (author, title, files or areas) before ranking.
