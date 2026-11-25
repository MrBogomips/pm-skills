---
name: release-plan
description: Drafts the release plan - the release goal, its scope cut into likely, at risk and unlikely by a Monte Carlo forecast of throughput, the 50/85/95% dates, release criteria, dependencies and approved changes - and revises it as the release nears. Use for "release plan", "plan the release", "what makes the release", "piano di rilascio", "pianifica il rilascio". Not the roadmap (product-roadmap).
---

# Release plan

Writes the plan of one release: what it is for, which items are likely to make it by the date and which are not,
when it is likely to ship, and what it has to meet before it goes out, every date from the forecast script.

## Inputs

- **The project register**: `PROJECT.md`, declared by `` - Project register: `PROJECT.md` `` in the project's
  `AGENTS.md` (or `CLAUDE.md`): `Project name`, `Internal code`, `Deliverable language`, the Profile keys
  `Definition of Done` and `Definition of Workflow`, the naming Conventions and the Registers. With no project
  register, suggest `/pm-skills:project-setup`; you may still draft in the session if the user wants, asking for
  what you would have read there and inventing no configuration.
- **Registers**, when declared: change log, decision log, risk register, capacity register, tools register,
  tailoring register.
- **Documents**: the latest product roadmap and the previous version of this release plan, found in the documents
  folder by the naming convention.
- **Tool capabilities** (through `TOOLS.md`): `issues` for the release's items in backlog order and the transition
  history (via the agent); `releases` for the release, its planned date and past releases.
- **Formats**: `${CLAUDE_PLUGIN_ROOT}/shared/documents/release-plan.md`,
  `${CLAUDE_PLUGIN_ROOT}/shared/documents/common.md` and
  `${CLAUDE_PLUGIN_ROOT}/shared/registers/flow-snapshot.md`.
- **Agent**: `flow-data-scout`.

## Steps

1. **Read the configuration** and the `## release-plan` section of `TAILORING.md`; say which rules you will apply.
2. **Set the release.** Its name and scope from the issues or releases tool (a fix version, a milestone), else from
   the user; the items not done, in backlog order, with what you counted and left out. The `target` date only when a
   source commits it (a contract milestone, a decision, an approved change request); otherwise there is none.
3. **Get the flow data.** Map the started states (every state from the start point up to the finish point), the
   finished states and the item types from the Definition of Workflow
   (else the board) and show the mapping. Offer the latest snapshot in the flow data folder of the Working documents
   section (else `flow/`) when it is recent; otherwise dispatch `flow-data-scout` with the path of `PROJECT.md`, a
   window of at least 180 days and the scope, validate its CSV in a temporary file named as the format says with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/flow_data.py" validate <file>`, show the path and the counts, and
   save it into the project only after the user agrees.
4. **Forecast.** Run `forecast.py when` for the number of items in scope, and with a target `forecast.py how-many`
   until the target:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/forecast.py" when <snapshot> --items N --started <states> --finished <states> --seed S`
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/forecast.py" how-many <snapshot> --until <target> --started <states> --finished <states> --seed S`
   Use the same seed for both and record it in Sources. Cut the ordered scope by the how-many lines as the format says. With no target, give only the `when` dates and cut no scope. Never compute a date or a count by hand.
5. **Gather the rest.** The Definition of Done (if missing, say so and list only release-level criteria); the
   approved change requests and decisions that touch the release; the open risks and dependencies; holidays and
   closures in the forecast window from the capacity register; the roadmap theme the release serves.
6. **Draft** in the format, in the `Deliverable language`, with the assumptions under their heading. When the
   committed scope falls beyond the 85% line at the target date, say so plainly under Dates and give the options the
   facts allow (cut scope, move the date, change through `/pm-skills:change-request`) without choosing. Keep facts
   apart from inferences; put in Sources what was read, with the date of the data, and what could not be read.
7. **Name and show.** Name the file with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/doc_naming.py" next --project <PROJECT.md> --dir <folder> --type release-plan --date <forecast day> --slug <release>`
   (exit status 3: a plan with that name exists; revise it instead). Show the draft and the path; write it with
   `status: draft`, `version: 1.0.0` only after the user agrees, and set `status: issued` when they approve it.
8. **Revise.** For a new version, rerun the forecast on a new snapshot, fill Changes from the previous version, raise
   the version with `doc_naming.py bump <version> major|minor|patch`, show the changes and write on agreement.

## Always

- Every forecast date comes with its percentiles and the snapshot it rests on.
- Commitments name their source; everything else is a forecast.
- Name every source that could not be read and what the plan cannot say because of it.

## Never

- Never change the release, the items, their order or their fix versions in the issues tool.
- Never choose between cutting scope and moving the date: the plan shows the options, the user decides.
- Never write to the registers from here: suggest `/pm-skills:change-request`, `/pm-skills:risk-register` or
  `/pm-skills:decision-log` for what they miss.

## Extension points

- `format`: sections added to or renamed in the plan, or a project template.
- `scale`: the percentile lines that cut the scope, the throughput history in weeks.
- `rules`: extra release criteria or an approval before the plan is issued.
- `steps`: extra steps before drafting or after issuing, such as a go/no-go check.
- `terms`: the project's words for the release, its scope bands and its criteria.
