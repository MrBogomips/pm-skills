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

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
