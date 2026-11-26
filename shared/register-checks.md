# Register checks

What the `register-reviewer` agent checks, register by register. Formats, keys and rules are in
`shared/registers/<register>.md`; each register's own validator covers its internal rules, so these checks only
cover what crosses a register boundary or the calendar. Each finding names the keeper that fixes it (the `Kept by:`
line of the register format, or the table in `shared/handoff.md`).

Severity: `blocking` (a reference to something that does not exist, a rule broken between registers),
`important` (a stale or contradicting value), `minor` (a gap or a drift worth tidying). A check whose register is not
declared in `PROJECT.md` is skipped and named as skipped, never reported as a finding.

## Consistency mode

Reads only the registers declared in `PROJECT.md` and the files they point to.

| Register | Checks |
|---|---|
| All | the validator of each declared register exits 0 (`validate <path>`); a declared file that does not exist; an ID reused or cited that no longer exists |
| `TEAMS.md` | the reference set for people: Active team slugs, History slugs; a History slug missing from Active team with no `To` date |
| `RISKS.md` | `Owner` is a slug of the Active team or a role of it or of the stakeholders; `Review` in the past on an open or occurred risk (overdue); a risk cited by a CR or a gate criterion exists |
| `DECISIONS.md` | `Decided by` slugs exist; `Supersedes` and `Superseded by` point to existing decisions that point back; a `superseded` decision has `Superseded by`; `Source` files exist |
| `CHANGES.md` | `Requested by` and `Decided by` slugs exist; `Decision` is an existing `D-NNN`; an `approved` change with no `Decision` when the decision log is declared; `Source` files exist; risks named in `Risk impact` exist |
| `RACI.md` | each role column matches a role in `TEAMS.md` or a stakeholder in `STAKEHOLDERS.md`; a role held by nobody on the Active team; one `A` per row (the validator checks it); `WBS` ids exist in the WBS document when one is in the documents folder |
| `STAKEHOLDERS.md` | `Owner` slugs exist; `Review` overdue on active rows; an `active` stakeholder with no row in `RACI.md` as a role, when both are declared |
| `GATES.md` | `Milestone` is an activity of `SCHEDULE.md` and is a milestone (duration 0); `Planned` agrees with that activity's `Finish` (same or earlier); a `passed` gate whose milestone has progress below 100; conditions of `go with conditions` with a date in the past and no later outcome |
| `SCHEDULE.md` | baseline `Change` cites an existing CR, approved; activities with progress below 100 and `Finish` in the past |
| `BUDGET.md` | role rates cover the roles of the Active team; a change cited exists and is approved |
| `CAPACITY.md` | members named exist in the Active team; periods of members who left (`To` in History) |
| `ACTIONS.md` | `Owner` slugs exist; `Status` is `open`, `done` or `dropped`; open rows with `Due` in the past (overdue); `Source` is a file that exists, a minutes ID or a URL; a `Tool` + `Item` pair, when present, has both; the ID `AC-NNN` is unique |
| `TOOLS.md` | a `file:` access whose file does not exist; a tool that `ACTIONS.md` names in `Tool` and that is not declared |

## Alignment mode

Compares the registers with facts the caller passes in, gathered by `project-activity-scout` or `flow-data-scout`.
Every finding quotes the fact it rests on, with its date. Facts missing for a check go in **Facts I lacked**.

| Register | Checks |
|---|---|
| `ACTIONS.md` | an open row with `Tool` + `Item` whose item is done or closed; a done row whose item is still open |
| `TEAMS.md` | an Active member with no activity in the window; an unmapped account that was active; a member with activity after their `To` date |
| `CHANGES.md` | an `approved` change with no work item, pull request or milestone movement since `Decided on`; an `implemented` change with no delivery fact |
| `RISKS.md` | a risk whose trigger, as written in `Risk`, already happened (an incident, a slipped release) and is still `open`; an `occurred` risk with no response progress |
| `SCHEDULE.md` | progress far behind or ahead of the done work items; a milestone passed in the facts but not at 100 |
| `GATES.md` | a gate planned in the window whose criteria cannot be supported by the facts |
| `DECISIONS.md` | a decision whose `Consequences` names work that the facts show was not started |
| `STAKEHOLDERS.md`, `RACI.md` | an owner or role with no delivery fact where the facts should show some |

An absence of activity is a question about the register, not a judgment of a person: state it about the entry.
