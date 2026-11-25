---
name: project-charter
description: Drafts and revises the project charter - purpose, objectives and success criteria, scope in and out, milestones, phases and gates, constraints, budget, risks, stakeholders and authority - from the registers, challenged by a critical review; proposes the initial risks, stakeholders and gates for the registers. Use for "project charter", "charter", "carta del progetto", "atto costitutivo del progetto".
---

# Project charter

Drafts the document that authorizes the project and that the project is then held to: why it exists, what it must
achieve, what it covers, within which constraints, and who has the authority to decide. The charter summarizes the
registers and seeds the empty ones.

## Inputs

- **Project register**: `PROJECT.md`, declared in the project's `AGENTS.md` (or `CLAUDE.md`) as
  `- Project register: \`<path>\``: the Identity (client, dates, contract type, language), the Profile, the naming
  Conventions and the Registers. With no project register, suggest `/pm-skills:project-setup`; you may still draft in
  the session if the user wants, asking for what you would have read there and inventing no configuration.
- **Registers, read**: stakeholders, risks, decisions, schedule (milestones), budget (lines and reserves), RACI,
  gates, changes, tailoring.
- **Documents**: the product roadmap, an earlier charter, contract or proposal summaries the user points to.
- **Formats**: `${CLAUDE_PLUGIN_ROOT}/shared/documents/project-charter.md` and
  `${CLAUDE_PLUGIN_ROOT}/shared/documents/common.md`; for the registers it seeds,
  `${CLAUDE_PLUGIN_ROOT}/shared/registers/risks.md`, `stakeholders.md` and `gates.md`.
- **Agent**: `pm-critical-reviewer`, before the charter is issued.

## Steps

1. **Read the configuration** and the `## project-charter` section of `TAILORING.md`; say which rules apply. Find an
   existing charter by the naming convention: if one is issued, go to step 7.
2. **Draft** in the format, in the `Deliverable language`, from the sources. Ask only for what they do not hold,
   typically the purpose, the objectives with their success criteria, what is out of scope and the authority of the
   project manager; never fill those with a guess. Each summary of a register points to it.
3. **Review.** Dispatch `pm-critical-reviewer` with the draft, its purpose and audience, the register paths and the
   facts read. When the charter goes to a steering committee or the client for approval, tell the user that the
   review goes to the agent with the model escalated to `fable`, because it is a deliverable for a steering
   committee or a client; the user may decline, and the review then runs on the agent's own model. Address its
   findings or show them to the user.
4. **Name and show.** Name the file with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/doc_naming.py" next --project <PROJECT.md> --dir <folder> --type project-charter --date <today>`.
   Show the draft, the path and the review's open points; write it with `status: draft`, `version: 1.0.0`, after the
   user agrees.
5. **Propose register entries**, only for registers declared in `PROJECT.md`, as one numbered list: the high-level
   risks not already in the risk register, the stakeholders not already in the stakeholder register, the phases'
   gates and their criteria not already in the gate register, each as a new row with the next free ID computed from
   the file and the values its format requires; a required value the charter does not give is asked, never made up.
   Write only the entries the user accepts, one register at a time, and validate each with its script in
   `${CLAUDE_PLUGIN_ROOT}/shared/scripts/` (`risks_register.py`, `stakeholders_register.py`, `gates_register.py`)
   until it exits 0. A change to an existing entry is listed with the skill that owns it; never edit it here.
6. **Issue** when the user reports the approval: set `status: issued`, `approved-by` and `approved-on` as the user
   states them, and fill the Approval heading. Suggest `/pm-skills:publish-deliverable` to share it.
7. **Revise** an issued charter only for an approved change: read it in the change log, name its ID in `change`,
   show the differences, and raise `version` with `doc_naming.py bump <version> major|minor` (major for scope,
   objectives or authority). Without an approved change, suggest `/pm-skills:change-request`.
8. **Report** what you read, what you inferred and what you could not read.

## Always

- Keep the registers authoritative: the charter summarizes them and says so.
- Show every write first and make it only after the user agrees; one write per register change.
- People appear as roles; no contacts and no evaluations.

## Never

- Never declare the charter approved, or fill `approved-by`, without the user's report of the approval.
- Never edit or delete an existing register entry, and never write the schedule register: its baselines belong to
  `schedule-check`.
- Never revise an issued charter without an approved change.
- Never apply a tailoring rule that loosens a guardrail; say that it was ignored and why.

## Extension points

- `format`: headings added to or renamed in the charter (a section the client requires), or a template.
- `rules`: extra checks, such as who must approve the charter or objectives that must be measurable.
- `steps`: extra steps before drafting, before the critical review, or after issuing.
- `terms`: the project's words for the charter and its parts.
