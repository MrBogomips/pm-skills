# Scenarios: product-roadmap

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **declared**: `AGENTS.md` with `- Project register: \`PROJECT.md\`` and a `## Working documents` section placing
  documents in `docs/`; `tests/fixtures/PROJECT.md` (coded naming, code `ACME`), `TOOLS.md`, `RISKS.md`,
  `DECISIONS.md` and `TAILORING.md` copied at the root; an issues tracker the session can read with invented epics
  for Acme Portal, and one planned release with a date.
- **previous roadmap**: **declared**, plus `docs/ACME-RM-001.md` with `horizons: now-next-later`,
  `version: 1.0.0`, `status: issued`.
- **no tools**: **declared**, with no `TOOLS.md`.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| first-draft-asks-goal | declared | "Draft the product roadmap" | Asks for the Product Goal and the themes (proposes wording, does not set them); asks now-next-later or dated; proposes name `docs/ACME-RM-001.md`; shows before writing; `status: draft`, `version: 1.0.0` |
| committed-vs-intended | declared | "Draft the product roadmap; the goal is self-service onboarding for Acme Corp's customers" | Items in the planned release are `committed` with the release as source; other epics `intended`; an epic with no theme listed for the user to place |
| revision-bumps-version | previous roadmap | "Aggiorna la roadmap: il tema reporting passa a Later" | Answers in Italian; revises `docs/ACME-RM-001.md` in place, version 1.1.0 from `doc_naming.py bump`; "Changes from the previous version" says what moved and why |
| no-forecast | declared | "Put a date on every theme" | Keeps dates only where committed; says the roadmap does not forecast and points to `/pm-skills:delivery-forecast` (planned) |
| no-epic-keys-invented | declared | "Add a theme for mobile access" | The item says it has no epic yet; no key is made up |
| no-tools | no tools | "Draft the product roadmap" | Says there is no tools register, suggests `/pm-skills:project-setup`, drafts from what the user says and names the sources it could not read |
| no-project-register | no project | "Product roadmap" | Suggests `/pm-skills:project-setup`; invents no configuration |
| handoff-not-write | declared | "Record the decision to drop the export from the roadmap" | Prepares a handoff proposal to `/pm-skills:decision-log`; does not write `DECISIONS.md` |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
