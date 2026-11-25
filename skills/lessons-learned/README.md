---
summary: For project managers and PMOs - writes the lessons learned of a project or a phase from retrospectives, gate outcomes, decisions, changes and risks, each point backed by a fact, with recommendations and owned follow-up actions, never about people.
---

# lessons-learned

Writes what a project or a phase learned: the context in facts, what worked, what did not, recommendations addressed
to the next phase, project or organization, and the actions the project itself will take.

## Why

Lessons learned sessions at the end of a project rely on memory, so they repeat the last month's frustrations and
lose what happened a year earlier, and they easily turn into a list of who did what wrong. This skill reads the trail
the project already left (retrospectives, gate outcomes, decisions, changes, risks), backs every point with a fact,
and keeps the document about the way of working.

## Use cases

### Close the project

**Context:** Acme Portal's closing gate passed; the project ran 24 sprints.

**Action:** Ask "write the lessons learned".

**Result:** A document with the objectives against the outcomes, the gate that was held once and why, the themes that
came back in several retrospectives, recommendations for the organization, and follow-up actions with owners and
dates.

### Learn from a phase

**Context:** The discovery phase ended with gate G-001.

**Action:** Ask "lezioni apprese della fase di discovery".

**Result:** The same document scoped to the phase, with `gate: G-001`.

## Usage

Ask in your own words ("lessons learned", "lezioni apprese") or run `/pm-skills:lessons-learned`.

## Inputs and outputs

- Reads `PROJECT.md`, `TAILORING.md`, the gate, decision, change, risk, schedule, budget and team registers, the
  retrospectives, gate reviews and status reports of the period, and the project's tools through `TOOLS.md`.
- Writes one lessons learned document in the folder of the project's Working documents section, named by
  `shared/scripts/doc_naming.py`, in the format of
  [`shared/documents/lessons-learned.md`](../../shared/documents/lessons-learned.md).

## Requirements

A project register (`/pm-skills:project-setup`). The richer the trail of retrospectives and gate reviews, the more the
document says.

## Limitations

- Never attributes a point to a person and drops or rephrases any point about one.
- Writes no register and no tool; risks and decisions it finds are suggested to the skills that own them.
