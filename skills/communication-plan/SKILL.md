---
name: communication-plan
description: Drafts and revises the communication plan - audiences, what each receives, when, through which channel and produced by which report or meeting, the meetings and the escalation path - from the stakeholder register, the RACI matrix and the reporting cadence; flags stakeholders left without communication. Use for "communication plan", "piano di comunicazione", "piano delle comunicazioni".
---

# Communication plan

Says who receives what, when, through which channel and from whom, so that every stakeholder the project depends on
is reached at the right level. It builds on the stakeholder register and the RACI matrix and never changes them.

## Inputs

- **Project register**: `PROJECT.md`, declared in the project's `AGENTS.md` (or `CLAUDE.md`) as
  `- Project register: \`<path>\``: `Project name`, `Internal code`, `Deliverable language`, `Reporting cadence`,
  `Agile framework`, `Sprint length`, the naming Conventions and the Registers. With no project register, suggest
  `/pm-skills:project-setup`; you may still draft in the session if the user wants, asking for what you would have
  read there and inventing no configuration.
- **Registers, read only**: the stakeholder register (roles, levels, engagement gap, approach, owner), the RACI matrix
  (roles consulted and informed per deliverable), the gate register (who decides gates), the tailoring register.
- **Documents**: the earlier communication plan, the project charter (authority, escalation).
- **Tools register**: tools with Purpose `publish` (how reports are distributed) and `meetings`.
- **Formats**: `${CLAUDE_PLUGIN_ROOT}/shared/documents/communication-plan.md` and
  `${CLAUDE_PLUGIN_ROOT}/shared/documents/common.md`.

## Steps

1. **Read the configuration** and the `## communication-plan` section of `TAILORING.md`; say which rules apply.
2. **Audiences**: the active stakeholders as roles or groups, with their register IDs, grouped where they need the
   same information; say what each needs to know, from its interest, influence and approach.
3. **Communications**: for each audience, what it receives, how often, through which channel and who owns it. Base
   the frequency on `Reporting cadence` and the sprint length; name what produces it (`status-report`,
   `sprint-review`, `meeting-minutes`, `phase-gate-review`) or "manual". Roles marked `C` or `I` in the RACI matrix
   receive what concerns their deliverables.
4. **Meetings and escalation**: the recurring meetings with their purpose, participants as roles, cadence and record;
   the escalation path from the charter's authority, or asked.
5. **Check** and report: active stakeholders below their desired engagement with no communication; stakeholders
   whose register approach names an action the plan does not carry; audiences flooded by several communications
   with the same content.
6. **Name and show.** Name the file with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/doc_naming.py" next --project <PROJECT.md> --dir <folder> --type communication-plan --date <today>`,
   or revise the existing plan in place (`doc_naming.py bump`). Show it; write after the user agrees, `status: draft`
   until they approve it, then `issued`.
7. **Report** what you read, inferred and could not read; suggest `/pm-skills:stakeholder-register` when an entry
   needs a new approach, owner or review.

## Always

- Audiences and owners are roles or groups; channels name the means, never an address.
- Cover every active stakeholder, or say why one is left out.
- Show before writing; write only after the user agrees.

## Never

- Never write email addresses, phone numbers or other personal contacts in the plan, and never suggest another
  project file for them: no register holds contacts; they live in the systems that own them (directory, mail).
- Never edit the stakeholder register, the RACI matrix or any other register.
- Never apply a tailoring rule that loosens a guardrail; say that it was ignored and why.

## Extension points

- `format`: headings or columns added or renamed, or a template.
- `rules`: extra checks, such as audiences that must receive every status report.
- `steps`: extra steps before drafting or after issuing.
- `terms`: the project's words for audiences, channels and meetings.
