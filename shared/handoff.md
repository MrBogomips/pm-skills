# Handoff to the keeper of a register

Every register has one keeper: the skill named on the `Kept by:` line of its format in `shared/registers/`. Only the
keeper writes the register. A skill that finds something another register should hold (a decision in a meeting, a
risk in a charter, a change request in a transcript, a follow-up for the project manager) does not write it: it
prepares a **handoff proposal** and hands it to the keeper, which checks it, computes the IDs, shows the change,
writes it and validates the register.

This is the only call from one skill of the plugin to another. Everything else composes through shared state.

## Keepers

| Register | File | Keeper |
|---|---|---|
| Project register | `PROJECT.md` | `project-setup` |
| Tools register | `TOOLS.md` | `project-setup` |
| Tailoring register | `TAILORING.md` | `pm-tailoring` |
| Team register | `TEAMS.md` | `team-register` |
| Capacity register | `CAPACITY.md` | `capacity-register` |
| Stakeholder register | `STAKEHOLDERS.md` | `stakeholder-register` |
| RACI matrix | `RACI.md` | `raci-matrix` |
| Decision log | `DECISIONS.md` | `decision-log` |
| Risk register | `RISKS.md` | `risk-register` |
| Change log | `CHANGES.md` | `change-request` |
| Gate register | `GATES.md` | `phase-gate-review` |
| Schedule register | `SCHEDULE.md` | `schedule-check` |
| Budget register | `BUDGET.md` | `budget-tracker` |
| Action log | `ACTIONS.md` | `action-log` |

The file names are the usual ones; the project register says where each register is.

**One exception.** A keeper that creates its register adds the line that declares it in the Registers section of
`PROJECT.md`, and nothing else there; `project_register.py validate` checks the result. Flow snapshots are data
files, not registers: the skills that compute them write them.

## The proposal

One block per entry, shown to the user with the rest of the skill's output, numbered when there are several:

```markdown
1. **Handoff to `/pm-skills:decision-log`**: add a decision
   - Register: `DECISIONS.md`
   - Source: `docs/ACME-MM-004-steering.md`
   - Raised by: `meeting-minutes`
   - Fields:
     - Date: 2026-11-24
     - Decided by: sponsor
     - Context: The payment provider's certification slipped to December.
     - Decision: Move the go-live of release 2.0 to 2027-01-15.
```

- **Change** is `add`, `update <ID>` or `close <ID>`, in the register's own terms (`supersede D-002`, `reassess
  R-004`).
- **Fields** use the register's keys, in English, with values in the project's language. A value the skill inferred
  ends with `(inferred)`. A field it could not fill is left out: the keeper asks for it, never the proposer.
- **No ID** for a new entry: the keeper computes it from the file just before writing.

## The flow

1. The proposing skill shows its proposals and asks which ones to hand off. The user may accept all, some or none.
2. For the accepted ones it says "Handing off to `/pm-skills:<keeper>`" and runs that skill with the proposals as
   its input, one keeper at a time. A keeper the user starts on purpose only (`project-setup`, `pm-tailoring`: their
   `disable-model-invocation` stops another skill from running them) is not run: print the proposals with the
   command `/pm-skills:<keeper>` ready to paste, and ask the user to run it.
3. The keeper treats a proposal as input, not as an order: it applies its own rules and steps, asks for what is
   missing, shows the change, writes on the user's agreement and validates. It reports the IDs it assigned. The
   user's acceptance in step 1 covers sending the proposal, not the change: the keeper always shows the change and
   waits for agreement before it writes.
4. The proposing skill resumes: it records those IDs where it links to them (the minutes, the charter) and reports
   what was handed off, what was written and what was declined.

A proposal the user declines is not written anywhere it would count as recorded. A skill may keep it as a note in
its own document when its format has a place for it.

## Never

- Never write, append to or edit a register you do not keep, even when the user asks: hand off instead.
- Never run a keeper without the user's agreement on the proposals it receives.
- Never hand off to a skill that does not keep the register, and never to a project skill: project skills do not
  edit the plugin's registers (`shared/integration-contract.md`).
