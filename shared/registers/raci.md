# RACI matrix format (`RACI.md`)

The RACI matrix says, for each deliverable or activity, which role is responsible for doing the work, which one is
accountable for it, and who is consulted or informed. Columns are roles or groups, never people: who holds a role is
in the team register. `raci-matrix` keeps it; `communication-plan`, `phase-gate-review` and `project-charter` read it.
It is declared in the Registers section of `PROJECT.md` as `` - RACI matrix: `RACI.md` ``.

Kept by: `raci-matrix`. Only this skill writes the register; any other skill hands its changes off to it, as
`shared/handoff.md` says.

## Example

```markdown
# RACI

| ID | Deliverable | WBS | Sponsor | Product owner | Tech lead | Developers | Security office |
|---|---|---|---|---|---|---|---|
| RA-001 | Payment flow | 1.2 | I | A | R | R | C |
| RA-002 | Go-live runbook | 3.1 | I | C | A/R | R | C |
| RA-003 | Release notes |  |  | A | C | R | I |
```

## Columns

The first three columns are fixed; the role columns that follow are the project's own, at least two.

| Column | Meaning | Rule |
|---|---|---|
| `ID` | stable identifier, never reused | `RA-` and at least three digits; unique |
| `Deliverable` | the deliverable or activity | not empty |
| `WBS` | the work package of the `wbs` document it belongs to | empty, or a dotted ID (`1`, `1.2`, `1.2.3`) |
| a role | a team register role or a stakeholder register entry (`Sponsor`, `Tech lead`, `Security office`) | distinct, not empty |

A role cell is empty or one of:

| Value | Meaning |
|---|---|
| `R` | responsible: does the work |
| `A` | accountable: answers for the result and approves it |
| `A/R` | accountable and responsible |
| `C` | consulted before the work is done or decided |
| `I` | informed once it is done or decided |

## Rules

1. Allowed lines: the title `# RACI`, blank lines and the table. There are no free notes: history is in git.
2. Each row has exactly one `A` or `A/R`, and at least one `R` or `A/R`.
3. Role columns name roles or groups, never a person's name or a team register slug; no cell or column holds an
   email address or a phone number.
4. Role names and `WBS` values are not checked against the other registers by the validator: `raci-matrix` reports
   the roles it cannot find in the team or stakeholder register and the work packages missing from the latest `wbs`
   document.
5. A row no longer relevant is removed; git keeps it.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/raci_register.py" validate <path to RACI.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
