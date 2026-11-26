---
title: pm-skills user guide
area: plugin
type: concept
---

# pm-skills user guide

This guide is for project managers and team leads who use the `pm-skills` plugin in their own projects. It explains
how the plugin thinks, how a project is laid out so that it works, and how to do the recurring jobs. It does not
cover installing the plugin: the repository's README does.

The examples follow an invented team: the Acme Portal project for the client Acme Corp, with the team members
`ada-l`, `bo-k` and `cy-t`.

## How the guide is organized

Pages are either **concept** pages (why and how it works) or **operational** pages (how to do a job). Each belongs
to an area: the plugin as a whole, or one of the seven performance domains of the PMBOK Guide.

| Page | Type | What it answers |
|---|---|---|
| [Skills](skills.md) | operational | Which skill do I ask for this job? |
| [Principles](principles.md) | concept | What will the plugin never do without me? |
| [Registers and their keepers](registers-and-keepers.md) | concept | Where does project state live and who may change it? |
| [Project folders](project-folders.md) | concept | How should my project be laid out? |
| [Meetings](meetings.md) | operational | How do I prepare, record and distribute a meeting? |
| [Actions and the PM backlog](actions-and-backlog.md) | operational | How do I track what I have to do? |
| [The inbox](inbox.md) | operational | How do I sort what lands in the project? |

## Where to start

Read [Principles](principles.md) and [Registers and their keepers](registers-and-keepers.md) once: they explain why
the skills behave as they do. Then run `/pm-skills:project-setup` in your project and use the [skill list](skills.md)
to pick the next job.
