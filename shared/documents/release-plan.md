# Document format: release plan (`release-plan`)

A release plan says what a release will contain and when it is likely to ship: its goal, its scope cut by
probability, the forecast dates, the criteria a release has to meet and what it depends on. It separates what the
project has committed from what the forecast only makes likely. The common rules (frontmatter, naming, versioning)
are in `shared/documents/common.md`.

A release plan is revised in place as the release approaches: each revision raises `version`, reruns the forecast on
a new snapshot and says what changed; the previous versions stay in git.

## Frontmatter

The common keys, plus:

| Key | Rule |
|---|---|
| `release` | the release as the issues or releases tool names it (`2.0`, `Portal December`), else a name the user gives |
| `snapshot` | the path of the flow snapshot the forecast was computed from, relative to the project root |
| `target` | the committed release date `YYYY-MM-DD`, only when a source commits it; absent otherwise |

`date` is the day the forecast was run.

## Headings

The headings below, in this order, translated into the document's language. A heading with nothing to say keeps a
one-line "nothing to report".

```markdown
# <Project name>: release plan <release>

## Release goal
## Scope
## Dates
## Release criteria
## Dependencies and risks
## Approved changes
## Assumptions
## Changes from the previous version
## Sources
```

| Heading | What goes there |
|---|---|
| Release goal | what the release gives its users, in one or two sentences, tied to the Product Goal or a roadmap theme when there is one |
| Scope | the items of the release in backlog order, by key and title, cut into `likely` (within the 85% line), `at risk` (between the 85% and the 50% line) and `unlikely` (beyond the 50% line) by the how-many forecast at the target date; with no target, the whole scope is one list and Dates carries the forecast |
| Dates | the when forecast for the scope: the 50%, 85% and 95% dates, the item count forecast, and the committed `target` with its source when there is one |
| Release criteria | the Definition of Done that every item meets, plus what the release as a whole needs (release notes, migration, sign-off), each with who confirms it as a role |
| Dependencies and risks | what the release depends on (other teams, the client, suppliers, environments, technical debt), with IDs from the risk register and the decision log |
| Approved changes | the change requests and decisions that changed the scope or the date, by `CR-NNN` or `D-NNN`, with what each changed |
| Assumptions | the forecast's assumptions: the throughput history window, a process that stays as it was, a scope that does not grow, and the holidays or closures in the forecast window |
| Changes from the previous version | what moved between scope bands, what was added or dropped and why, how the dates moved |
| Sources | the snapshot, the registers and tools read, with the date of the data, and the ones that could not be read |

## Rules

- **Forecast, not promise.** Every date and every cut comes from the plugin's forecast script and is given with its
  percentiles; the plan never shows a single forecast date on its own.
- **Committed or forecast.** A date or an item is committed only when a source says so: a contract milestone, a
  decision in the decision log, an approved change request. The Sources say where each commitment comes from. When
  the forecast puts the committed scope beyond the 85% line at the target date, the plan says so under Dates.
- Items, releases and IDs are those of the issues tool and the registers, never made up.
- The order of the scope and the release goal are the Product Owner's decisions: the plan records them.
- No person appears as the owner of an item or in a judgment; release criteria name roles.
