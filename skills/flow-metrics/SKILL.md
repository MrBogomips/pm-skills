---
name: flow-metrics
description: Computes the team's flow metrics from the work items' transition history - cycle time percentiles, throughput, WIP, work item age against the SLE - saves a snapshot to compare over time, and DORA metrics if possible. Team level, never per person. Use for "flow metrics", "cycle time", "throughput", "aging items", "DORA"; not for forecasts (delivery-forecast).
---

# Flow metrics

Measures how work flows through the team's workflow, from a saved snapshot of the transition history, and explains
what the numbers say: how long items take, how many finish, how much is in progress and which items are aging.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **The project register**: `PROJECT.md`, declared by `` - Project register: `PROJECT.md` `` in the project's
  `AGENTS.md` (or `CLAUDE.md`): `Project name`, `Deliverable language`, the Profile keys `Definition of Workflow`
  and `Agile framework`, and the Registers. With no project register, suggest `/pm-skills:project-setup`; you may
  still compute from data the user gives, asking for the workflow mapping and inventing no configuration.
- **Registers**, when declared: tools register, tailoring register.
- **The Definition of Workflow** file: the work item types, the started and finished points, the states, the WIP
  limits and the Service Level Expectation (SLE). When the file is missing, fall back to the board's configuration
  and say so.
- **Tool capabilities** (through `TOOLS.md`): `issues` for the transition history (via the agent); `releases`,
  `code`, `ci` and `incidents` for DORA.
- **Formats**: `${CLAUDE_PLUGIN_ROOT}/shared/registers/flow-snapshot.md` (snapshot and DORA inputs).
- **Agent**: `flow-data-scout`.

## Steps

1. **Read the configuration** and the `## flow-metrics` section of `TAILORING.md`; say which rules you will apply.
2. **Map the workflow.** From the Definition of Workflow (else the board): the started states (every state from the
   start point up to the finish point, not only the first) and the finished states, the item types in scope.
   Ask for what is missing. Express the SLE as days and percent (`85% of items in 10 days` gives
   `--sle-days 10 --sle-percent 85`). Show the mapping. A state listed in the snapshot but in neither list stays
   before the start.
3. **Get the data.** Snapshots are in the folder the project's Working documents section gives for flow data (else
   `flow/`), named as the format says. Offer the latest one when it is recent enough for the question; otherwise
   dispatch `flow-data-scout` with the path of `PROJECT.md`, the window (default 180 days) and the scope, and wait
   for its report, including its Coverage, Gaps and Sources checked.
4. **Save the snapshot.** Put the agent's CSV in a temporary file named as the format says (the date in the
   name is the snapshot's today) and run
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/flow_data.py" validate <file>`; on errors, show them and stop.
   Show the path, the number of items and rows, and the date range; write it into the project only after the user
   agrees. A snapshot of the same day is replaced only on agreement; git keeps the old one.
5. **Compute.** Run
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/flow_metrics.py" <snapshot> --started <states> --finished <states> [--from D] [--to D] [--today D] [--sle-days N --sle-percent P]`
   and show its working. Never compute, round or extrapolate a metric by hand.
6. **Explain**, team level, in the user's language: cycle time percentiles and what the 85th means for a new item;
   the throughput trend and its spread; WIP now against the limits; the items in progress past the SLE, or close
   to it, by key, as candidates for the team's attention. Point to likely causes only as questions for the team
   (blocked items, a growing queue in one state, WIP above the limit), and keep what the data shows apart from what
   you infer.
7. **Compare**, when an earlier snapshot exists or the user asks: run
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/flow_metrics.py" compare <old> <new> --started <states> --finished <states> [--weeks N] [--sle-days N]`
   with the same mapping (`--weeks` gives both the same window length), and say what moved. A change of mapping between the two makes them incomparable: say so.
8. **DORA**, when the tools allow: deployments with their dates (`releases`), the commit time of each deployed change
   (`code`), failed deployments (`ci` or `releases`) and incidents with their restore time (`incidents`). Write them
   to temporary files as the format's DORA inputs (never into the project) and run
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/dora.py" --deployments <file> [--incidents <file>] --from D --to D`.
   Leave out each metric whose data is missing, and say which.
9. **Close** with the Sources: snapshot path and date, mapping used, tools read and not read, the agent's Gaps.
   Suggest `/pm-skills:delivery-forecast` for dates and `/pm-skills:retrospective` to discuss the findings.

## Always

- Metrics are the team's; items appear by key and title, never with who works on them.
- Show the script's output or the lines that matter from it, so the numbers can be checked.
- Say how much history the numbers rest on (weeks, finished items) and when it is too little to read a trend.
- Name every source that could not be read and what the metrics cannot say because of it.

## Never

- Never compare, rank or single out people, and never add a person column to a snapshot or a DORA input.
- Never compute a metric without the scripts, and never fill a gap in the history with a guess.
- Never change the board, the items or the Definition of Workflow; suggest `/pm-skills:project-setup` for the
  Definition of Workflow.

## Extension points

- `scale`: the default window, the percentiles to stress, the "close to the SLE" threshold.
- `rules`: extra checks, such as item types always excluded or states never counted as finished.
- `steps`: extra steps after computing, such as posting a summary through a declared tool.
- `terms`: the project's words for the states, the SLE and the metrics.
