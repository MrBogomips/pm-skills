# Gate register format (`GATES.md`)

The gate register keeps the project's phase gates: the points where the people with the authority decide whether
the project may go on, the criteria each gate is judged on, and every outcome decided, so that the state and the
history of a gate are in one file. `phase-gate-review` keeps it; `project-charter` proposes new gates for it, and
`lessons-learned` reads it. It is declared in the Registers section of `PROJECT.md` as
`` - Gate register: `GATES.md` ``.

## Example

```markdown
# Gates

## Gates

| ID | Gate | Milestone | Planned | Status |
|---|---|---|---|---|
| G-001 | Discovery exit | A-004 | 2026-03-13 | passed |
| G-002 | Go-live readiness | A-010 | 2026-11-27 | passed |

## Criteria

| Gate | # | Criterion |
|---|---|---|
| G-001 | 1 | Product Goal and first release scope approved by the sponsor |
| G-002 | 1 | Release scope meets the Definition of Done |
| G-002 | 2 | No open risk scored high without a response |
| G-002 | 3 | Security office sign-off on the payment flow |

## Outcomes

| Gate | Date | Outcome | Decided by | Conditions | Review |
|---|---|---|---|---|---|
| G-001 | 2026-03-13 | go | steering committee |  | ACME-GR-001.md |
| G-002 | 2026-11-13 | hold | steering committee | Criterion 3 not met | ACME-GR-002.md |
| G-002 | 2026-11-27 | go with conditions | steering committee | Pen test fixes by 2026-12-11 (criterion 3) | ACME-GR-003.md |
```

## Gates

| Column | Meaning | Rule |
|---|---|---|
| `ID` | stable identifier, never reused | `G-` and at least three digits; unique |
| `Gate` | the name of the gate | not empty |
| `Milestone` | the schedule register activity the gate sits on | empty, or an activity ID (`A-004`); not checked against `SCHEDULE.md` |
| `Planned` | the date the gate is planned for | empty or `YYYY-MM-DD`; may change after an outcome |
| `Status` | `open`, `passed` or `stopped` | consistent with the last outcome (below) |

## Criteria

| Column | Meaning | Rule |
|---|---|---|
| `Gate` | the gate the criterion belongs to | an ID of `## Gates` |
| `#` | the number of the criterion within its gate | a whole number from 1; unique within the gate |
| `Criterion` | what must be true to pass, stated so that evidence can show it | not empty |

Every gate has at least one criterion.

## Outcomes

| Column | Meaning | Rule |
|---|---|---|
| `Gate` | the gate decided | an ID of `## Gates` |
| `Date` | the day of the decision | `YYYY-MM-DD` |
| `Outcome` | the decision | `go`, `go with conditions`, `hold` or `stop` |
| `Decided by` | the role or body that took it (steering committee, sponsor) | not empty |
| `Conditions` | what must happen, and by when, for the decision to stand; for a hold, what is missing | required for `go with conditions` and `hold` |
| `Review` | the gate review document, relative to the documents folder, as `doc_naming.py` prints it | optional; not checked for existence |

## Rules

1. Allowed lines: the title `# Gates`, the three sections in the order of the example, each once, blank lines and
   one table per section. There are no free notes: the reasoning is in the gate review document, history in git.
2. A gate's `Status` is `passed` when its last outcome is `go` or `go with conditions`, `stopped` when it is `stop`,
   and `open` when it has no outcome or the last one is `hold`.
3. The outcomes of a gate are in date order; two on the same day are allowed.
4. No outcome follows `go` or `stop`. After `go with conditions`, a later `go` records that the conditions were met,
   and a `hold` or `stop` that the pass was withdrawn. After `hold`, any outcome may follow.
5. Outcomes are appended, never edited or removed. The criteria of a gate that has an outcome are not changed: a gate
   whose criteria must change after a decision becomes a new gate. The validator cannot see history, so
   `phase-gate-review` enforces this rule; git keeps the record.
6. An outcome is written only when the people with the authority have decided it: the register records decisions,
   never an assessment.
7. No cell holds an email address or a phone number.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/gates_register.py" validate <path to GATES.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
