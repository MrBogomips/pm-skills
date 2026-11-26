# Tailoring register format (`TAILORING.md`)

The tailoring register holds the project's own rules for the plugin's skills: a risk scale, an approval, a section a
client wants in every report, the project's words for things. Each rule sits on an extension point that the skill
declares in the **Extension points** section of its `SKILL.md`. The register is declared in the Registers section of
`PROJECT.md` as `` - Tailoring register: `TAILORING.md` ``; rules can be written by hand.

Kept by: `pm-tailoring`. Only this skill writes the register; any other skill hands its changes off to it, as
`shared/handoff.md` says.

## Example

```markdown
# Tailoring

## risk-register

### scale

- Probability and impact from 1 to 5; a score of 15 or more is high and goes to the steering committee.

## status-report

### format

- After "Risks and issues", add a section "Client actions" with what Acme Corp has to provide.

### terms

- The status report is called "highlight report" in titles.
```

## Extension points

| Point | What a project may change |
|---|---|
| `format` | the headings or the template of the document the skill writes |
| `scale` | scoring scales and thresholds |
| `rules` | extra checks or approvals |
| `steps` | extra steps at the named points the skill offers (for example before drafting, before writing) |
| `terms` | the project's vocabulary |

To list the points each skill declares:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/tailoring_register.py" points
```

## Rules

1. Allowed lines: the title `# Tailoring`, blank lines, one `## <skill>` section per skill, `### <point>` headings
   under it, and the rules (any text, usually bullets) under each heading.
2. A skill is a skill of the plugin that declares extension points; a point is one the skill declares. Each appears
   once.
3. A point has at least one rule.
4. No rule holds an email address or a phone number.
5. **No rule loosens a guardrail.** The people rule, writes only through `write` tools after the user agrees, showing
   before writing, and naming the sources that could not be read always apply. A skill ignores a rule that would
   loosen one, and says so.

## How skills use it

A skill reads its own section at the start, applies each rule at its point, and says which rules it applied. A rule
that contradicts the skill's format or the register's schema (a column the validator rejects, for example) is not
applied; the skill says why and suggests changing it.

## Validation

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/tailoring_register.py" validate <path to TAILORING.md>
```

Exit status 0 means valid; 1 prints one error per line as `line N: <message>`; 2 means the file could not be read.
