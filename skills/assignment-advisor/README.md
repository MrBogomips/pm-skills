---
summary: For project managers and tech leads - suggests who should take a task or review a pull request or document, with reasons, from the team register, and assigns only on your agreement.
---

# assignment-advisor

Suggests up to three people from your team register for a task, a pull request review or a document review, each
with the reasons: matching areas, recent activity in the repositories involved, open load. It assigns or requests a
review only when you agree, and only through a tool your project declares for writing.

## Why

Picking a reviewer or an assignee often defaults to whoever comes to mind, and misses the people who know the area.
This skill grounds the choice in the register's areas and in recent activity, leaves out the author, anyone who
already approved and the current assignee, and tells you where its data was missing.

## Use cases

### Pick a reviewer for a pull request

**Context:** A pull request in `acme/web` is waiting for review.

**Action:** Ask "who should review acme/web#42?".

**Result:** Up to three candidates with their areas, recent reviews in `acme/web` and open load; the author and
existing approvers are left out, with a line saying so.

### Assign a task

**Context:** A new issue, `ACME-123`, touches the payment API.

**Action:** Ask "who should take ACME-123?", then "assign it to Ada".

**Result:** A ranked list; after you pick, the skill shows the assignment and makes it through the issue tracker if
`TOOLS.md` declares it `write`, otherwise it gives you the step to do it yourself.

## Usage

Ask in your own words or run `/pm-skills:assignment-advisor` with the work (an issue key, a pull request, a document
path or a sentence).

## Inputs and outputs

- Reads `PROJECT.md`, the team register and the tools register; reads the work through the project's `issues` and
  `code` tools; dispatches the `project-activity-scout` agent for recent activity.
- Writes no files. Writes to a tool only through one declared with `Mode: write`, after you confirm the exact change.

## Requirements

- A project register (`/pm-skills:project-setup`) and a team register (`/pm-skills:team-register`).
- A tools register with `issues` and `code` tools for activity data; without them the skill asks for the details of
  the work and ranks on the register alone.

## Limitations

- Considers only the active members of the register.
- Ranks by areas and recent activity; open load only breaks ties, and open review load is not counted.
