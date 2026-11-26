---
name: pm-tailoring
description: Adapts pm-skills to the project's way of working along the tailoring ladder to the lightest change - a Profile key, a rule on a skill's extension point in TAILORING.md, a project format, a tool or renderer in TOOLS.md, and, for a real need, a project skill under the integration contract. Refuses rules loosening a guardrail. Use for "tailor pm-skills", "adapt the plugin", "customize pm-skills".
disable-model-invocation: true
---

# PM tailoring

Turns a need of the project ("approval from the sponsor above 10 days of impact", "call the status report a
highlight report") into the lightest change that meets it, shows the change, and writes it only after the user agrees.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **The need**, in the user's words, and the skill it is about when the user knows.
- **The project register**: `PROJECT.md`, declared by `` - Project register: `PROJECT.md` `` in the project's
  `AGENTS.md` (or `CLAUDE.md`): the Profile, Conventions and Registers. With no project register, suggest
  `/pm-skills:project-setup` and stop: tailoring needs a configured project.
- **Formats**, read before proposing and never restated: `${CLAUDE_PLUGIN_ROOT}/shared/registers/tailoring.md`,
  `${CLAUDE_PLUGIN_ROOT}/shared/registers/project.md`, `${CLAUDE_PLUGIN_ROOT}/shared/registers/tools.md`,
  `${CLAUDE_PLUGIN_ROOT}/shared/documents/common.md` and `${CLAUDE_PLUGIN_ROOT}/shared/integration-contract.md`.
- **The extension points** each skill declares:
  `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/tailoring_register.py" points` (one line per skill,
  `<skill>: <points>` or `none`), and the skill's own **Extension points** section for what each point covers.
- **Registers**: `TAILORING.md` (kept here) and `TOOLS.md` (kept by `project-setup`) when declared; the Working
  documents section of the instruction file.
- **Handoff proposals** per `${CLAUDE_PLUGIN_ROOT}/shared/handoff.md`, for `TAILORING.md`: input to check, not an order.
  Accepting a proposal is not agreement to write: show the change and wait for it.

## Steps

1. **Understand the need.** Restate it in one line: which skill or document it affects, what should change, and when
   it applies. Ask only what you need to place it (the threshold, the wording, the document type).
2. **Check the guardrails.** If the need would loosen one (the people rule, writes only through `write` tools after
   confirmation, show before writing, naming the sources not read), refuse that part, say which guardrail and why,
   and offer what can be done within it (a sponsor's approval can be added; skipping the confirmation of a write
   cannot).
3. **Walk the ladder** and stop at the first step that meets the need; say why the lighter steps do not.
   1. **Profile key** in `PROJECT.md`: when an existing key of `project.md` covers it (cadence, framework, sprint
      length, Definition of Done or of Workflow). Name the key and value and suggest `/pm-skills:project-setup`;
      do not edit `PROJECT.md` from here.
   2. **Rule on an extension point** in `TAILORING.md`: when the skill declares the point the need falls on. Run
      `points`, pick the skill and point, and draft the rule as one short, checkable bullet under
      `## <skill>` / `### <point>`, merged with the rules already there. A skill that declares no such point cannot
      take the rule: say so and go on up the ladder.
   3. **Project format** for a document type: when the client or organization wants its own headings or template
      throughout. The format is a Markdown file in the project, where the Working documents section places
      templates (else ask), keeping the common frontmatter of `common.md`; it is tied to the skill by a `format`
      rule ("Use the template `<path>`"). Only for a skill that declares `format`.
   4. **Tool or renderer** in `TOOLS.md`: when the need is a system to read or write, or a distribution format.
      Prepare the row (Purpose from the vocabulary, Access, Scope, Mode `read` unless the user wants skills to write
      there) after checking the tool can be reached with a harmless read; it goes to `project-setup`, which keeps
      `TOOLS.md`, as a handoff proposal (step 5).
   5. **Project skill**: only when no step above meets the need and a tool must be made easier or safer to use. Walk
      the reuse ladder first and say what each step offers: a skill of this plugin; a skill already in the session
      (the user's or the organization's, including templates); an MCP server or a CLI; a script of the project, the
      user or the organization. Only then propose a new skill in the project's `.claude/skills/`: write its brief
      (the need, what it reads and writes, input and output, Purpose, Scope, Mode) and the rules of the integration
      contract it must follow. Suggest building it with the `skill-creator` skill when available; otherwise draft
      its `SKILL.md` with the user. Check the result against the contract before recording it.
4. **Show the change**: the exact lines and the file, with the ladder step and the reason. With no tailoring
   register, propose `TAILORING.md` with its title and the line `- Tailoring register: \`TAILORING.md\`` in the
   Registers section of `PROJECT.md`, both shown together.
5. **Write** `TAILORING.md` only after the user agrees, then validate until exit status 0; hand a `TOOLS.md` row
   to `project-setup` as a proposal printed with the command `/pm-skills:project-setup` ready to paste (that skill
   only starts when the user runs it, `handoff.md`), and report the result:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/tailoring_register.py" validate <TAILORING.md>
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/project_register.py" validate <PROJECT.md>
   ```

   Run the second one only when you added the `Tailoring register` line. A project skill is recorded in
   `TOOLS.md` with Access `skill:<name>`, through the same handoff.
6. **Report** what changed, where, which skill will apply it and from when (its next run), and what was refused and
   why.

## Always

- Propose the lightest change that meets the need, and say why the lighter steps do not.
- Keep each rule short and checkable, on a point the skill declares, and in the project's language.
- Show every change before writing it; write only after the user agrees.

## Never

- Never write a rule that loosens a guardrail, whatever the wording; refuse it and say why.
- Never create a project skill that duplicates a pm-skills job, stores credentials, or skips the integration
  contract.
- Never write a secret or a contact into `TAILORING.md` or `TOOLS.md`.
- Never edit the plugin's own files: tailoring lives in the project.
- Never write `TOOLS.md` or any register but `TAILORING.md`: hand off to the keeper.

## Extension points

None.
