---
name: raci-matrix
description: Keeps the project's RACI matrix (RACI.md) - for each deliverable or activity, which role is responsible, accountable, consulted and informed - built from the charter, the WBS and the team and stakeholder roles, with exactly one accountable role per row; answers who is accountable for what. Use for "RACI", "responsibility matrix", "who is accountable for", "matrice RACI", "chi è responsabile di".
---

# RACI matrix

Keeps `RACI.md`: who does the work, who answers for it, who is consulted and who is informed, for each deliverable or
activity, by role. Roles survive turnover; who holds a role is in the team register.

## Inputs

- **Project register**: `PROJECT.md`, declared in the project's `AGENTS.md` (or `CLAUDE.md`) as
  `- Project register: \`<path>\``. The matrix is its `- RACI matrix: \`<path>\`` line under Registers. With no
  project register, suggest `/pm-skills:project-setup`; if the user wants to go on in the session, work on a path
  they name and invent no configuration.
- **Format**: `${CLAUDE_PLUGIN_ROOT}/shared/registers/raci.md`, the single source for columns, values and rules.
  Read it before writing; do not restate it to the user.
- **Tailoring**: the `## raci-matrix` section of the tailoring register, when declared.
- **Read only**: the team register (the `Roles` column, never people), the stakeholder register (roles and groups),
  the latest `wbs` document (work package IDs and names) and the latest `project-charter` (deliverables), found in
  the documents folder by the naming convention.

## Steps

1. **Start.** Read the project register, the matrix and the tailoring section; say which tailoring rules apply.
2. **Set up** (no matrix, or the user asks): propose `RACI.md` at the project root (or where the Working documents
   section places registers) and the line `- RACI matrix: \`RACI.md\`` for `PROJECT.md`. Show both, write after the
   user agrees, then validate `PROJECT.md` with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/project_register.py" validate <path>`.
3. **Propose rows and columns.**
   - Rows: the work packages of the latest `wbs` (with their ID in `WBS`), else the deliverables of the charter,
     else what the user names. Skip those already in the matrix.
   - Columns: the roles of the team register and the stakeholder roles that take part in the work or its approval
     (sponsor, client roles, a security office). Ask the user to confirm the set; keep it short.
   - Letters: propose one `A` per row, with the reason from a source (the charter's authority, an approval in the
     decision log); the user decides. A row where no role can be accountable is asked, never guessed.
4. **Check against the registers** and report, without changing them: role columns found in neither the team nor
   the stakeholder register; `WBS` values missing from the latest `wbs` (renumbered or removed packages); roles in
   the team register with no letter anywhere.
5. **Write.** New rows get the next ID: the highest `RA-` number plus one, never reused. Show the rows (or the
   changed cells), write after the user agrees, then validate:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/raci_register.py" validate <path>` and fix until it exits 0.
6. **Answer** questions such as "who is accountable for the runbook?" or "what is the Tech lead responsible for?"
   from the matrix, naming the role; add who holds it from the team register only when the user asks.

## Always

- **Roles, never people**: columns are roles or groups. When the user names a person, ask for the role they hold
  and use that; the person stays in the team register.
- **One accountable**: exactly one `A` (or `A/R`) per row, at least one `R` (or `A/R`).
- **Show before writing**: every change to `RACI.md` or `PROJECT.md` is shown first and written after the user
  agrees; one write per change.
- **Facts apart from inferences**: say what was read, what was inferred and which sources were unavailable.
- Talk in the user's language, or the project's `Deliverable language`; the title, column headers `ID`,
  `Deliverable`, `WBS` and the letters stay as the format says.

## Never

- Never use a person's name, slug, email address or phone number as a column or in a cell.
- Never write the team register, the stakeholder register or the `wbs` document; report what does not match.
- Never set an `A` the user has not confirmed.
- Never apply a tailoring rule that loosens a guardrail; say that it was ignored and why.

## Extension points

- `rules`: extra checks, such as roles that must be consulted on every release deliverable, or no `A/R` rows.
- `terms`: the project's words for the roles and for responsible, accountable, consulted and informed.
