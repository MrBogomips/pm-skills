---
summary: For project managers - adapts pm-skills to the project's way of working with the lightest change that does it, from a rule in TAILORING.md to a project skill that follows the integration contract.
---

# pm-tailoring

Takes a need of your project, such as a sponsor's approval above a threshold or your own name for a document, and
finds the lightest change that meets it: a Profile key, a rule on a skill's extension point, a project format, a tool
or renderer, or, only when nothing else does, a project skill. It shows the change and writes it after you agree.

## Why

Every project bends the standard a little: a client wants a section in every report, a steering committee wants to
see risks above a score, a team says "SAL". Doing this by editing skills breaks on the next update; doing it in
scattered notes means skills ignore it. This skill puts each need where the plugin's skills read it, validates it,
and refuses any rule that would loosen a guardrail, such as skipping the confirmation of a write.

## Use cases

### Add an approval to change requests

**Context:** The client wants the sponsor's approval for any change with more than 10 days of impact.

**Action:** Run `/pm-skills:pm-tailoring` and say "changes over 10 days of impact need the sponsor's approval".

**Result:** A `rules` entry under `change-request` in `TAILORING.md`, shown first, written after you agree and
validated.

### Use the project's name for a document

**Context:** The team calls status reports "SAL".

**Action:** Say "call status reports SAL".

**Result:** A `terms` rule under `status-report`; the skill also points out that the document code can be set in the
Conventions of `PROJECT.md` through `/pm-skills:project-setup`.

### Publish in the organization's Word format

**Context:** Deliverables must go out in the organization's Word template and no renderer is declared.

**Action:** Say "we need status reports in our Word template".

**Result:** The reuse ladder first (an available skill, a CLI such as a converter, a script); only if none fits, a
brief for a project skill that follows the integration contract, recorded in `TOOLS.md` as a `publish` tool.

## Usage

Run `/pm-skills:pm-tailoring` and describe the need. The skill is invoked only on purpose.

## Inputs and outputs

- Reads `PROJECT.md` (declared in `AGENTS.md` or `CLAUDE.md`), `TAILORING.md`, `TOOLS.md`, the Working documents
  section, and the extension points each skill declares.
- Writes rules to `TAILORING.md` in the format of
  [`shared/registers/tailoring.md`](../../shared/registers/tailoring.md), tools to `TOOLS.md`, project formats as
  templates in the project, and project skills under `.claude/skills/` following
  [`shared/integration-contract.md`](../../shared/integration-contract.md), each after you agree.

## Requirements

A project register (`/pm-skills:project-setup`).

## Limitations

- A rule can sit only on an extension point the skill declares; a need outside them climbs the ladder.
- Profile keys and conventions go through `/pm-skills:project-setup`; in `PROJECT.md` this skill only adds the
  `Tailoring register` line, when it creates the register.
- No rule may loosen a guardrail; such requests are refused with the reason.
