# Budget register format (`BUDGET.md`)

The budget register holds the project's approved budget, line by line, with its reserves, the rates per role used to
cost effort, and the approved changes to the budget. `budget-tracker` keeps it, and `estimate` reads its rates. It is
declared in the Registers section of `PROJECT.md` as `` - Budget register: `BUDGET.md` ``.

Kept by: `budget-tracker`. Only this skill writes the register; any other skill hands its changes off to it, as
`shared/handoff.md` says.

## Example

```markdown
# Budget

Currency: EUR
Last reviewed: 2026-11-20

## Lines

| ID | Line | Kind | Amount | From | To |
|---|---|---|---|---|---|
| B-001 | Development and design | labor | 182000.00 | 2026-01-12 | 2026-12-18 |
| B-002 | Cloud hosting | expense | 14400 | 2026-01-12 | 2026-12-18 |
| B-003 | Contingency reserve | contingency | 12000 | 2026-01-12 | 2026-12-18 |
| B-004 | Management reserve | management reserve | 10000 | 2026-01-12 | 2026-12-18 |

## Rates

| Role | Rate | Unit | From |
|---|---|---|---|
| developer | 520 | day | 2026-01-12 |
| tester | 55 | hour | 2026-01-12 |
| developer | 540 | day | 2026-07-01 |

## Approved changes

| Date | Line | Amount | Change |
|---|---|---|---|
| 2026-11-04 | B-001 | +8100.00 | CR-002 |
```

## Fields

| Field | Meaning | Rule |
|---|---|---|
| `Currency` | the currency of every amount | required; an ISO 4217 code, three capital letters |
| `Last reviewed` | the last day the budget was checked against actuals | optional; `YYYY-MM-DD` |
| Lines `ID` | the budget line | `B-` and at least three digits, unique, in increasing order |
| Lines `Line` | what the money is for | not empty |
| Lines `Kind` | `labor` and `expense` are the budget; `contingency` (the reserve for known risks) and `management reserve` (the reserve for the unforeseen) are reserves | `labor`, `expense`, `contingency` or `management reserve` |
| Lines `Amount` | the amount approved for the line | a number not below zero, at most 15 digits before the point and two decimals, a point as decimal mark and no thousands separator |
| Lines `From`, `To` | the period the line covers | `YYYY-MM-DD`; `To` not before `From` |
| Rates `Role` | a role of the team register | not empty; a role, never a person |
| Rates `Rate` | the cost of one unit of work of the role | a number above zero, at most two decimals |
| Rates `Unit` | `hour` or `day` | `hour` or `day` |
| Rates `From` | the first day the rate applies | `YYYY-MM-DD`; a later row of the same role supersedes it from its own `From` |
| Approved changes `Date` | the day the change to the budget was approved | `YYYY-MM-DD` |
| Approved changes `Line` | the budget line it changes | the `ID` of a line |
| Approved changes `Amount` | the amount added to the line, or taken from it with `-` | a signed number, not zero, at most two decimals |
| Approved changes `Change` | the approval | a change request (`CR-NNN`) or a decision (`D-NNN`) |

A line's current amount is its `Amount` plus its approved changes. The **budget at completion** (BAC) is the sum of
the `labor` and `expense` lines; the reserves are reported apart and never count in it. Drawing on a reserve is two
approved changes with the same reference: a negative one on the reserve and a positive one on the line it funds.

## Rules

1. Allowed lines: the title `# Budget`, blank lines, `Currency:` and `Last reviewed:` before the sections, and the
   sections `## Lines`, `## Rates` and, optionally, `## Approved changes`, in this order, each with its table. There
   are no free notes.
2. The headers are exactly the ones in the example. Two rates of the same role never share `From`.
3. No line's current amount is below zero.
4. The register holds the cost of roles, never of a person: there is no column for names, and no rate is set for one
   person. No cell holds an email address or a phone number.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/budget_register.py" validate <path to BUDGET.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
The validator does not read the team register or the change log: `budget-tracker` checks that every role is a role
of the team and every `CR-NNN` or `D-NNN` exists.

## Earned value

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/budget_register.py" evm <path to BUDGET.md> \
    --status-date YYYY-MM-DD (--pv N --ev N --ac N | --data <CSV>) [--eac-cpi-spi]
```

The command computes the earned value figures at the status date, against the BAC of the register with the approved
changes dated up to the status date:

- planned value (PV), earned value (EV) and actual cost (AC) are cumulative amounts in the register's currency,
  given on the command line or read from a CSV file with the header `date,pv,ev,ac` and one row per period; the row
  used is the latest on or before the status date, and the earlier rows show the trend of CPI and SPI;
- cost variance CV = EV − AC, schedule variance SV = EV − PV, cost performance index CPI = EV / AC, schedule
  performance index SPI = EV / PV;
- estimate at completion EAC = BAC / CPI and, with `--eac-cpi-spi`, also EAC = AC + (BAC − EV) / (CPI × SPI);
  estimate to complete ETC = EAC − AC; variance at completion VAC = BAC − EAC; to-complete performance index
  TCPI = (BAC − EV) / (BAC − AC).

Amounts are computed in decimal and shown with two decimals, indices with two decimals; a figure that would divide by
zero is shown as `n/a`. The reserves are listed apart. The output is plain text and shows each formula with its
numbers. Exit status 0 on success; 1 when the register or the CSV file is invalid (the errors go to stderr) or no
CSV row falls on or before the status date; 2 on a usage error or a file that cannot be read.
