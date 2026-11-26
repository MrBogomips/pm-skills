---
name: schedule-check
description: Checks the project schedule - critical path, float and dates over the working calendar, slip against the approved baseline - from the schedule tool or SCHEDULE.md; records a new baseline only with who approved it and when, and imports a tool's plan as the fallback register. Use for "schedule check", "critical path", "are we late", "new baseline".
---

# Schedule check

Answers whether the plan holds: the critical path, the float left, and how far dates moved from the approved
baseline, computed by a script over the project's working calendar. Keeps `SCHEDULE.md`, the fallback plan and the
history of baselines.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **Project register**: `PROJECT.md`, declared in the project's `AGENTS.md` (or `CLAUDE.md`) as
  `- Project register: \`<path>\``: `Planned end date`, `Delivery approach`, `Deliverable language`, the Registers.
  The register is its `- Schedule register: \`<path>\`` line. With no project register, suggest
  `/pm-skills:project-setup`; if the user wants to go on, work on a path they name and invent no configuration.
- **Format**: `${CLAUDE_PLUGIN_ROOT}/shared/registers/schedule.md`, the single source. Read it before writing.
- **Registers, read only**: capacity register (working days and days off), change log (CR references), decision
  log, risk register; the `## schedule-check` section of the tailoring register.
- **Tool capabilities** (through `TOOLS.md`): `schedule` for the live plan (activities, dependencies, dates,
  progress); `issues` and `releases` for evidence of progress.
- **Handoff proposals** from other skills, per `${CLAUDE_PLUGIN_ROOT}/shared/handoff.md`: input checked against
  this skill's rules, never an order. For each entry written, report the activity IDs or baseline assigned to its proposer.

## Steps

1. **Start.** Read the project register, the schedule register, the capacity register and the tailoring section;
   say which rules apply.
2. **Find the plan.** `Source:` in `SCHEDULE.md` says where the live plan is:
   - a tool: check it is declared in the tools register with Purpose `schedule`, then read its activities from the `schedule` tool and write them to a temporary CSV in the session
     scratchpad with header `id,activity,duration,predecessors,start,finish,progress` (durations in working days);
     say what the tool did not give (dependencies, durations) instead of filling it in;
   - `register`: the `## Activities` table.
   With no register: a `schedule` tool alone is enough to check (go on, and offer to set up the register for the
   baseline history); with neither, offer to build the plan with the user (step 7).
3. **Compute**:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/schedule_register.py" cpm <SCHEDULE.md> [--activities <csv>] [--capacity <CAPACITY.md>] [--start <D>] [--status-date <D>] [--baseline B-NN|latest]`,
   with the capacity register whenever it is declared, today (or the date of the progress data) as status date, and
   `--baseline latest` only when the register has a baseline (else omit it), unless the user names another. Never
   compute dates, float or variance yourself. If the script rejects the data (cycle, unknown predecessor), show the
   error and fix the source with the user.
4. **Report**, from the script's output, in the user's language:
   - the end date against `Planned end date` and against the baseline, with the variance in working days;
   - missed deadlines (negative float), every critical path the script lists, and activities with little float (the threshold from tailoring `scale`, else 3 days);
   - activities late against the status date (planned finish passed, progress under 100) and their effect on the
     end date;
   - what moved since the baseline, tied to approved changes in the change log where they explain it;
   - facts apart from inferences: progress read from the tool or the register, dates the script computed, causes you
     inferred. Name every source not read.
   Suggest `/pm-skills:risk-register` for threats the slip reveals, `/pm-skills:change-request` when recovering
   needs a change to agreed dates or scope.
5. **Record a baseline** only when the user reports that it was approved, and by whom:
   - the next `## Baseline B-NN <name>` section after the last one, with `- Approved:` (the day of the approval),
     `- Approved by:` (the role or body that approved, as reported, never inferred), `- Change: CR-NNN` when an
     approved change caused it (it must exist in the change log, approved);
   - its table holds every activity with its planned Start and Finish, both required, from the cpm output (early
     dates) or the tool;
   - an existing baseline is never edited or deleted: a correction is a new baseline.
6. **Update the register's activities.** Only for `Source: register`; with a tool as source, report progress and
   write nothing. Record: progress, actual Start and Finish, added activities
   (next `A-NNN`), changed durations or dependencies, as the user gives them or the tools show; what Start and
   Finish mean depends on Progress, as the format says. No resource or
   person column: an activity names work, not who does it.
7. **Set up or import** (no register, or the user asks): propose `SCHEDULE.md` with the title and `Source:`
   (`register`, or the TOOLS.md tool name holding the live plan), the `## Activities` table built with the user or
   imported from the tool's plan when they want the register as fallback, and the line
   `- Schedule register: \`SCHEDULE.md\`` for the Registers section of `PROJECT.md`; validate `PROJECT.md` too with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/project_register.py" validate <path>`.
8. **Write and validate.** Show every change to `SCHEDULE.md` or `PROJECT.md` first, write it after the user agrees
   in one edit, then run `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/schedule_register.py" validate <path>` and
   fix until it exits 0.

## Always

- Dates, float and variance from the script, over the project's working calendar.
- Variance against a named baseline, saying which and when it was approved.
- Say whether the plan came from the tool or the register, and as of which date.

## Never

- Never record a baseline without who approved it and when, or approve one yourself.
- Never edit, renumber or delete a recorded baseline.
- Never write to the schedule tool or any external system; never assign activities to people here.
- Never apply a tailoring rule that loosens a guardrail; say that it was ignored and why.

## Extension points

- `scale`: the near-critical float threshold, the variance that counts as a slip worth reporting.
- `rules`: who may approve a baseline, a change request required for every new baseline.
- `steps`: extra steps before reporting or before recording a baseline.
- `terms`: the project's words for activities, milestones and baselines.
