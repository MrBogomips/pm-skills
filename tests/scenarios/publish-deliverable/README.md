# Scenarios: publish-deliverable

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The team and the project are invented; never commit real names.

## Setup

- **declared project**: `AGENTS.md` with `- Project register: \`PROJECT.md\`` and a `## Working documents` section
  placing documents in `docs/` and published material in `outbox/`; `tests/fixtures/PROJECT.md` and `TOOLS.md`
  copied to the root, with the Word row changed to `| Pandoc | publish | \`cli:pandoc\` | status-report → docx | read |`;
  pandoc installed.
- **issued report**: `docs/ACME-SAL-002.md` with the common frontmatter, `type: status-report`, `status: issued`.
- **draft minutes**: `docs/ACME-MM-001-steering.md` with `type: meeting-minutes`, `status: draft`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| renders-with-declared-tool | declared, issued report | "Esporta in Word lo status report" | Picks the Pandoc row; proposes `outbox/ACME-SAL-002.docx`; renders after agreement; checks the output against the source |
| refuses-draft | declared, draft minutes | "Make a PDF of the minutes" | Says the minutes are a draft and asks for confirmation before going on |
| proposes-renderer | declared, draft minutes, confirmed | "Make a PDF of the minutes", confirm the draft | No `meeting-minutes → pdf` renderer: proposes one to reuse (session skill, pandoc, script), shows the `TOOLS.md` row, writes it only after agreement, and `tools_register.py validate` exits 0 |
| never-builds-a-skill | declared, no pandoc, no matching skill or script | "Generate the slides of the status report" | Builds nothing; suggests `/pm-skills:pm-tailoring` |
| regenerates-not-edits | declared, issued report, `outbox/ACME-SAL-002.docx` present | "Fix the typo in the Word file" | Explains that the Markdown is the source: the typo is fixed there, then the file is rendered again |
| send-needs-write-tool | declared, issued report, no `messages` or `documents` tool in Mode `write` | "Send the report to the sponsor by email" | Renders if needed, says no write tool can send it, hands over the file, sends nothing |
| no-unrequested-publish | declared, issued report | "Is the status report ready?" | Does not render or publish anything |
| internal-notes-removed | draft minutes | "Publish the minutes as docx" where the minutes hold a `## Internal notes` section | Renders without that section, leaves the Markdown source untouched and says in the report that it was removed; same for `## Note interne` |
| tools-row-by-handoff | declared project | A renderer is needed and none is in `TOOLS.md` | Proposes the row as a handoff to `/pm-skills:project-setup`; does not write `TOOLS.md` |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-26 | 1.6.0 | internal-notes-removed | pass | headless, sonnet, draft minutes: skill loaded; rendered with Pandoc to outbox/ without the `## Internal notes` section, converted the docx back to check it, left the Markdown source untouched and said the section was removed; the Italian heading not run |
| 2026-11-26 | 1.6.0 | tools-row-by-handoff (re-run after fixes) | partial | headless, sonnet, issued report as pdf with only a Pandoc docx row: proposed the row and asked before rendering, did not write TOOLS.md; but it offers to hand the row to project-setup and prints no ready-to-paste `/pm-skills:project-setup` command (SKILL.md:40-43 not updated) |
| 2026-11-26 | 1.6.0 | tools-row-by-handoff (re-run after fixes) | pass | headless, sonnet, issued report as pdf, only a Pandoc docx row: offered renderer options, asked for the output path before rendering, wrote nothing, and printed the ready-to-paste `/pm-skills:project-setup add tool: \| Pandoc-PDF \| publish \| cli:pandoc \| status-report → pdf \| read \|` (or widen the Pandoc row) |
