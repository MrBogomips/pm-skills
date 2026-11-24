# Risk register format (`RISKS.md`)

The risk register records the project's threats and opportunities, how likely and how serious each one is, the
response chosen and who owns it. `risk-register` keeps it; `status-report` and `meeting-minutes` read it. It is
declared in the Registers section of `PROJECT.md` as `` - Risk register: `RISKS.md` ``.

## Example

```markdown
# Risks

Scale: 1-5
Last reviewed: 2026-11-20

| ID | Type | Risk | Category | Probability | Impact | Score | Strategy | Response | Owner | Status | Raised | Review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R-001 | threat | If the payment provider's sandbox stays unstable, integration tests slip and the release moves | dependency | 4 | 4 | 16 | mitigate | Contract tests against a local stub; weekly check with the provider | ada-l | open | 2026-10-01 | 2026-12-01 |
| R-002 | opportunity | If the client approves the shared design system, the web team can reuse its components | scope | 2 | 4 | 8 | enhance | Demo at the next sprint review | bo-k | open | 2026-11-02 | 2026-12-10 |
| R-003 | threat | If the staging environment is not ready by October, load tests cannot start | release | 5 | 3 | 15 |  | Environment ready on 2026-10-20 |  | closed | 2026-09-01 |  |
```

## Fields

| Field | Meaning | Rule |
|---|---|---|
| `Scale` | the range of Probability and Impact | optional, default `1-5`; `<low>-<high>`, high at most 10 |
| `Last reviewed` | the last date the whole register was reviewed | optional; `YYYY-MM-DD` |
| `ID` | stable identifier, never reused | `R-` and at least three digits; unique |
| `Type` | `threat` or `opportunity` | |
| `Risk` | the risk as cause, event and effect ("If …, then …") | not empty |
| `Category` | the source of the risk: for example technical debt, dependency, release, supplier, scope, people, budget | free text |
| `Probability`, `Impact` | the assessment on the scale | whole numbers within the scale |
| `Score` | Probability × Impact | exactly the product |
| `Strategy` | threats: `avoid`, `mitigate`, `transfer`, `accept`, `escalate`; opportunities: `exploit`, `enhance`, `share`, `accept`, `escalate` | required for open and occurred risks |
| `Response` | the actions of the response, or what happened when the risk was closed | free text |
| `Owner` | who watches the risk and carries out the response: a team register slug or a role | required for open and occurred risks |
| `Status` | `open`, `occurred` (it happened and is being handled) or `closed` | |
| `Raised` | the date the risk was recorded | `YYYY-MM-DD` |
| `Review` | the next review date | `YYYY-MM-DD`, not before Raised; required for open and occurred risks |

## Rules

1. Allowed lines: the title `# Risks`, blank lines, `Scale:`, `Last reviewed:` and the table. There are no free
   notes: context goes in the cells, history in git.
2. The header is exactly the one in the example.
3. A closed risk stays in the table with its last assessment; it is never deleted.
4. No cell holds an email address or a phone number, and no cell judges a person: a risk about people is stated as a
   delivery fact ("If the only reviewer of the API is unavailable in December, …").

Thresholds (what counts as high) are not part of the format: they come from the `scale` extension point in
`TAILORING.md`, or the skill's default.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/risks_register.py" validate <path to RISKS.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
