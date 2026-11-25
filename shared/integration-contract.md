# Integration contract for project skills

A project skill is a skill in a project's `.claude/skills/`, built for a real need after the reuse ladder in
`DESIGN.md` ("Tailoring"): a Word document in the organization's format, an email in the client's layout, a
ticketing system with its quirks. It makes a tool easier or safer to use; it never duplicates a pm-skills job. The
plugin's skills reach it as a tool, through `TOOLS.md`, and rely on what follows. A project skill that does not
respect this contract is not recorded in `TOOLS.md`.

## Declaration in `TOOLS.md`

One row per use, in the format of `shared/registers/tools.md`:

| Column | Value |
|---|---|
| `Tool` | the name the team uses for it |
| `Purpose` | the capabilities it offers, from the register's vocabulary (`publish` for a renderer) |
| `Access` | `skill:<name>`, where `<name>` is the frontmatter `name` of the skill and its directory |
| `Scope` | what it covers: for a renderer `<document type> → <format>` (`status-report → docx`), else the system, project or channel it reaches |
| `Mode` | `write` when it writes to an external system (sends, uploads, creates or changes items), `read` otherwise |

## What the skill states

Its `SKILL.md` says, near the top:

- **Reads**: the files, registers and systems it reads.
- **Writes**: the files it writes in the project and the external systems it writes to.
- **Input** and **Output**: what it expects from the caller and what it produces.

## What the skill respects

1. **Show before writing.** Every file it writes in the project is shown first, or its path and content summarized,
   and written only after the user agrees.
2. **Confirm external writes.** Every write to an external system is shown exactly (what, where, to whom) and made
   only after the user confirms; several writes are confirmed on an itemized list. It writes externally only when its
   row says `Mode: write`.
3. **No credentials.** It never stores, prints or asks to record a secret: tokens, passwords and keys stay in the
   environment or the tool's own login. No contact details in project files beyond work accounts.
4. **People rule.** No sensitive personal data and no evaluations of people in what it reads back, writes or sends:
   delivery facts only.
5. **Renderers take the plugin's Markdown.** A `publish` skill takes as input a Markdown document written in the
   format of `shared/documents/<type>.md`, renders it as it is (no content added, removed or reworded), keeps the base
   name of the source with the format's extension, and writes its output where the project's Working documents
   section places distribution formats, else where the caller says.
6. **Report what it did.** It ends by saying what it read, what it wrote or sent and where, and what it could not do
   and why; a failure is reported, never hidden or replaced by a guess.
7. **Stays in scope.** It does not edit the plugin's registers, does not invoke the plugin's skills, and does not
   loosen any of the plugin's guardrails through its own instructions.
