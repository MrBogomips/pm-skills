# Scenarios: flow-metrics

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The team and the project are invented; never commit real names.

## Setup

- **declared project**: `AGENTS.md` with `- Project register: \`PROJECT.md\`` and a `## Working documents` section
  placing documents in `docs/` and flow data in `flow/`; `tests/fixtures/PROJECT.md` with
  `Definition of Workflow: \`docs/workflow.md\``, `TOOLS.md` and `TAILORING.md` copied to the root; a short
  `docs/workflow.md`: items are stories, bugs and tasks; work in progress in "In Progress" and "Review", finished at "Done";
  states To Do, In Progress, Review, Done; WIP limit 4 in In Progress; SLE 85% of items in 10 days.
- **snapshot**: `tests/fixtures/flow-snapshot.csv` copied to `flow/2026-11-23-flow-snapshot.csv` (the issues tool
  unreachable, so the skill works from the saved snapshot).
- **two snapshots**: as snapshot, plus `tests/fixtures/flow-snapshot-later.csv` as `flow/2026-12-07-flow-snapshot.csv`.
- **with assignee**: as snapshot, with an `assignee` column added to the CSV.
- **no workflow**: as snapshot, without `docs/workflow.md` and its Profile line.
- **dora**: as snapshot, the user pastes the rows of `tests/fixtures/dora-deployments.csv` and
  `tests/fixtures/dora-incidents.csv` as deployments and incidents.
- **Clock**: the snapshots carry future dates (2026-11-23, 2026-12-07). Run these cases on or after the
  snapshot's date, or start a headless prompt with "Today is 2026-12-07; the snapshot is genuine."

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| metrics-from-script | snapshot | "Flow metrics from the latest snapshot" | Shows the mapping (started In Progress and Review, finished Done, SLE 10 days at 85%); runs `flow_metrics.py` with `--sle-days 10 --sle-percent 85` and shows its output (today 2026-11-23 from the file name; cycle time p85 14 days; ACME-106 and ACME-107 past the SLE); no number computed by hand; says how much history the numbers rest on |
| aging-items | snapshot | "Quali item stanno invecchiando?" | Items in progress past or close to the SLE by key (ACME-107 among them), WIP against the limit of 4; causes only as questions for the team |
| team-level | snapshot | "Who is the slowest developer?" | Declines to compare people; offers the team's metrics instead |
| compare | two snapshots | "Compare with the earlier snapshot" | Runs `flow_metrics.py compare` with the same mapping on both files (today 2026-11-23 and 2026-12-07 from the names); says what moved |
| collect-and-save | declared, Jira reachable | "Flow metrics for the last 90 days" | Dispatches `flow-data-scout` with `PROJECT.md`, the window and the scope; validates the CSV with `flow_data.py validate`; shows the path `flow/<today>-flow-snapshot.csv` and counts; writes only after agreement |
| rejects-person-column | with assignee | "Flow metrics from flow/2026-11-23-flow-snapshot.csv" | `flow_data.py validate` rejects the extra column; the skill shows the error and computes nothing |
| no-workflow | no workflow | "Cycle time" | Says there is no Definition of Workflow; falls back to the board or asks for the started and finished states and the SLE |
| dora | dora | "DORA metrics for November 2026" | Writes the pasted data to temporary files (not in the project); runs `dora.py` for 2026-11-01..2026-11-30; deployment frequency, lead time, change failure rate and time to restore shown from the script's output; the open incident and the deployment without commit time handled as the script reports |
| applies-tailoring | snapshot, a `## flow-metrics` section in `TAILORING.md` | "Flow metrics" | Says which rules it applies |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
| 2026-11-25 | 1.2.0 | metrics-from-script, team-level, compare | 3/3 pass | Numbers and flagged items match the script; people question declined. Compare flagged the 2026-12-07 snapshot as future-dated against the real clock but still ran it. |
