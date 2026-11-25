# Stakeholder register format (`STAKEHOLDERS.md`)

The stakeholder register records who has a stake in the project, how much they care about it and can affect it,
how engaged they are against how engaged the project needs them to be, and what the project does about the gap.
An entry is a role or a group first ("Sponsor", "End users"); the organization and a person's name are optional.
`stakeholder-register` keeps it; other skills read it. It is declared in the Registers section of `PROJECT.md` as
`` - Stakeholder register: `STAKEHOLDERS.md` ``.

## Example

```markdown
# Stakeholders

Last reviewed: 2026-11-10

| ID | Stakeholder | Organization | Name | Interest | Influence | Current | Desired | Approach | Owner | Status | Review |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S-001 | Sponsor | Acme Corp |  | high | high | supportive | leading | Monthly steering demo of the release plan; early notice of budget changes | Project manager | active | 2026-12-15 |
| S-002 | End users | Acme Corp |  | high | low | unaware | supportive | Beta programme and release notes inside the portal | bo-k | active | 2026-11-20 |
| S-003 | Security office | Acme Corp |  | medium | high | neutral | neutral |  | ada-l | active | 2027-01-15 |
| S-004 | Payment provider | Initech |  | medium | medium | supportive | supportive |  |  | inactive |  |
```

## Fields

| Field | Meaning | Rule |
|---|---|---|
| `Last reviewed` | the last date the whole register was reviewed | optional; `YYYY-MM-DD` |
| `ID` | stable identifier, never reused | `S-` and at least three digits; unique |
| `Stakeholder` | the role or group: sponsor, steering committee, end users, a supplier | not empty |
| `Organization` | the organization the stakeholder belongs to | optional, free text |
| `Name` | a person's name, when the role is held by one known person | optional, free text |
| `Interest` | how much the project's outcome matters to them | `low`, `medium` or `high` |
| `Influence` | how much they can affect the project | `low`, `medium` or `high` |
| `Current` | their engagement today | `unaware`, `resistant`, `neutral`, `supportive` or `leading` |
| `Desired` | the engagement the project needs from them | same values as `Current` |
| `Approach` | what the project does to move or keep their engagement: actions, never traits of the person | required when `Current` differs from `Desired` |
| `Owner` | who keeps the relationship: a team register slug or a role | required for active rows |
| `Status` | `active` or `inactive` (no longer relevant to the project) | |
| `Review` | the next review date | `YYYY-MM-DD`; required for active rows |

The engagement values are ordered from `unaware` to `leading`: a stakeholder is below the desired engagement when
`Current` comes before `Desired` in that order.

## Rules

1. Allowed lines: the title `# Stakeholders`, blank lines, `Last reviewed:` and the table. There are no free notes:
   context goes in the cells, history in git.
2. The header is exactly the one in the example.
3. An inactive stakeholder stays in the table; it is never deleted.
4. No cell holds an email address or a phone number: contacts live in the systems that own them. Assessments are
   levels only, and no cell comments on a person: `Approach` says what the project does, not what someone is like.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/stakeholders_register.py" validate <path to STAKEHOLDERS.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
