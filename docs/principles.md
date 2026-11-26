---
title: Principles
area: plugin
type: concept
---

# Principles

The plugin follows a few rules in every skill. They tell you what to expect and what it will refuse to do, even if
you ask.

## You decide, the plugin proposes

A skill drafts, analyses and suggests. It does not take decisions that are yours: who approves a change request,
who owns an action, whether a risk is high enough to act on. When a fact is missing, it asks instead of guessing.

## Show before writing

Every write in your project is shown first and made only after you agree. A bulk operation is confirmed on the
itemized list. The same holds for the changes a skill proposes to another skill's register: you see them first
(see [Registers and their keepers](registers-and-keepers.md)).

## Writes to other systems go through declared tools only

A skill writes to an external system (a comment, an assignment, a status change, a published file, a sent message)
only through a tool the project declared in `TOOLS.md` with `Mode: write`, and only after you confirm that write.
A tool declared `read` is never written to. Skills that only collect facts never write.

## It says what it read, inferred and could not reach

Every output separates what was read from a source, what was inferred and what was unavailable. A skill never
fills a gap with a guess: it names the source it could not read, for example an issue tracker it has no access to.

## People: delivery facts only

Project files live in a repository that others read. They never hold sensitive personal data (health, the reason
for an absence, contacts beyond work accounts, individual cost) or evaluations of people (judgments, appraisals,
personal notes). They may hold what the project needs: availability by period with no reason given, and delivery
performance as measurable facts. A skill that suggests who should take or review work does it to assign, never to
appraise, and gives its reasons.

## Capabilities, not tools

Skills do not depend on a particular system. A skill asks for a capability (such as `issues`, `code` or `publish`)
and uses whichever tool of the project offers it. Which systems you use, how they are reached and whether skills
may write to them is declared once, in `TOOLS.md`, which `project-setup` keeps. Without it, a skill tells you which
sources it could not read.

## Numbers come from scripts

Earned value, critical path, three-point estimates, forecasts, flow metrics and date arithmetic are computed by
tested scripts that ship with the plugin, not by the model's own arithmetic. When a skill shows a figure, a script
produced it.

## Language and the Italian glossary

You can write to the skills in any language: they answer in yours, and write documents in the project's
`Deliverable language` when `PROJECT.md` sets one. In Italian, skills use the terms of a shared glossary, the
same word every time, and keep in English the words Italian teams keep. A project's own vocabulary, recorded in its
tailoring register, comes first: a team that calls its status report "SAL" keeps that word.

## Adapting the plugin

You can adapt a skill to the way your project works with `/pm-skills:pm-tailoring`, which chooses the lightest
change that does the job. It will not write a rule that loosens any principle above: it can add a sponsor's
approval, but it cannot remove the confirmation of a write.
