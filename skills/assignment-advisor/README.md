---
summary: For project managers and tech leads - suggests who should take a Jira task or review a pull request or document, with reasons, from the team register.
---

# assignment-advisor

Suggests up to three people from your team register for a Jira task, a pull request review or a document review,
each with the reasons: matching areas, recent activity in the repositories involved, open Jira load. It never
assigns or requests anything itself.

## Why

Picking a reviewer or an assignee often defaults to whoever comes to mind, and misses the people who know the area.
This skill grounds the choice in the register's areas and in recent activity, leaves out the author, anyone who
already approved and the current assignee, and tells you where its data was missing.

## Usage

Ask "who should review acme/web#42?", "chi prende ACME-123?", "who should review docs/design.md?" or describe the task
in a sentence, or run `/pm-skills:assignment-advisor` with the work. The answer is a short ranked list with the
reasons; if you ask it to go ahead, it gives you the command to run, such as
`gh pr edit 42 --repo acme/web --add-reviewer <login>`.

## Requirements

- A team register, created with [`team-register`](../team-register/README.md).
- To read a pull request, the `gh` CLI logged in; to read a Jira task, an Atlassian MCP server or the `acli` CLI.
  Without them the skill asks you for the details of the work and ranks on the register alone.

## Limitations

- Suggests only: never assigns, requests reviews or comments on GitHub or Jira.
- Considers only the active members of the register.
- Ranks by areas and recent activity; open Jira load only breaks ties, and open review load is not counted.
