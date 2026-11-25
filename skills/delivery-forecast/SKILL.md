---
name: delivery-forecast
description: Forecasts when a number of work items will be done, or how many will be done by a date, with a simulation over the team's weekly throughput from a saved snapshot, always as 50/85/95% ranges with their assumptions. Use for "when will it be done", "how many items by", "forecast", "quando finiamo", "quando sarà pronto", "previsione di consegna", "quanti item entro".
---

# Delivery forecast

Answers "when will these items be done?" and "how many will be done by then?" with probabilities, from the team's
own throughput history, and states what the forecast assumes so the reader knows when it stops holding.

## Inputs

- **The project register**: `PROJECT.md`, declared by `` - Project register: `PROJECT.md` `` in the project's
  `AGENTS.md` (or `CLAUDE.md`): `Project name`, `Deliverable language`, the Profile key `Definition of Workflow`,
  and the Registers. With no project register, suggest `/pm-skills:project-setup`; you may still forecast from data
  the user gives, asking for the workflow mapping and inventing no configuration.
- **Registers**, when declared: tools register, tailoring register, capacity register (closures and holidays in the
  forecast window, to mention).
- **The Definition of Workflow** file: the item types and the started and finished points; else the board's
  configuration, and say so.
- **Tool capabilities** (through `TOOLS.md`): `issues` for the transition history (via the agent) and for the items
  still to do in a scope (a release, an epic, a filter).
- **Formats**: `${CLAUDE_PLUGIN_ROOT}/shared/registers/flow-snapshot.md`.
- **Agent**: `flow-data-scout`.

## Steps

1. **Read the configuration** and the `## delivery-forecast` section of `TAILORING.md`; say which rules you will
   apply.
2. **Frame the question.** `when` (a number of items, from a start date, by default the day after the
   snapshot's date, `--start`) or `how many` (by a date).
   For `when`, count the items still to do from the issues tool for the scope the user names, or take the number
   they give; say which items you counted and which you left out (done, cancelled, other types). Ask when the scope
   is unclear.
3. **Map the workflow**: the started states (every state from the start point up to the finish point), the finished
   states and the item types, from the Definition of Workflow (else the board); show the mapping. The forecast counts the same item types the throughput counts.
4. **Get the data.** Snapshots are in the folder the project's Working documents section gives for flow data (else
   `flow/`), named as the format says. Offer the latest one when it is recent; otherwise dispatch `flow-data-scout`
   with the path of `PROJECT.md`, a window covering at least the throughput history (default 180 days) and the
   scope, then validate its CSV in a temporary file named as the format says with
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/flow_data.py" validate <file>`, show the path and the counts, and
   save it into the project only after the user agrees.
5. **Run the forecast.**
   - when: `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/forecast.py" when <snapshot> --items N --started <states> --finished <states> [--weeks-history 12] [--start D] [--type T] --seed S`
   - how many: `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/forecast.py" how-many <snapshot> --until D --started <states> --finished <states> [--weeks-history 12] [--type T] --seed S`
   Pass a seed and report the one the output prints, so a rerun with it repeats exactly; `--type`
   forecasts one item type only. Never compute, interpolate or round a date or a count by hand.
6. **Present** in the user's language: the 50%, 85% and 95% lines, with what each means ("85%: done on or before
   this date in 85% of runs"; for how many, "at least this many in 85% of runs"). Recommend the 85% line for a
   commitment and say why. Then the assumptions, every time:
   - the history window used (weeks, and the weeks with zero throughput it contains);
   - the process stays as it was in that window: same team size, same WIP, same mix of item types;
   - the scope does not grow: items split or added later move the dates, so rerun when the backlog changes;
   - holidays and closures in the forecast window, from the capacity register, that the history did not have.
   Flag a history that is too short or too uneven to trust (the script's warnings, fewer than about ten weeks, a
   recent change of team or workflow).
7. **Close** with the Sources: snapshot path and date, mapping, scope and items counted, tools not read. Suggest
   `/pm-skills:release-plan` to turn the forecast into a plan.

## Always

- Give every forecast as a range of probabilities, with its assumptions and the snapshot it comes from.
- Forecast the team's throughput as a whole, never an individual's.
- Name every source that could not be read and what the forecast cannot say because of it.

## Never

- Never give a single date or count without the percentiles, and never present the 50% line as a commitment.
- Never forecast from story points or estimates through this skill: it counts items; suggest `/pm-skills:estimate`
  for estimates.
- Never compute a forecast without the script, and never change the board or the items.

## Extension points

- `scale`: the throughput history in weeks, the percentiles shown, the line recommended for commitments.
- `rules`: extra checks, such as a minimum history before a forecast is given, or item types always excluded.
- `steps`: extra steps after the forecast, such as recording it in the decision log.
- `terms`: the project's words for items, throughput and the forecast lines.
