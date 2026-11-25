---
summary: For project managers - builds the work breakdown structure and its dictionary from the charter or roadmap, checked against the 100% rule, and creates work packages as work items on confirmation.
---

# wbs-builder

Decomposes the project's whole scope into deliverables and work packages, with a dictionary of descriptions,
acceptance and accountable roles. It keeps the IDs stable so the RACI matrix and estimates can point to them, and warns
you when a revision breaks those references.

## Why

A WBS drawn once on a whiteboard misses scope the charter promised, adds scope nobody approved, and its numbers drift
so that nothing else can refer to them. This skill decomposes from the approved scope source, checks that every part
of it is covered and nothing more, says where it could not check, and treats a renumbering as a major revision that
lists what it breaks.

## Use cases

### Break down the scope at planning

**Context:** Acme Portal's charter is issued; the issues tool declared in `TOOLS.md` holds five epics.

**Action:** Ask "build the WBS".

**Result:** An outline with dotted IDs that keeps the epics as a level, a dictionary per work package, the
exclusions from the charter under Out of scope, and the places where the 100% rule could not be checked.

### Create the work packages in the tracker

**Context:** The WBS is approved and Jira is declared with Mode `write`.

**Action:** Ask "create the work packages in Jira" (Italian works too).

**Result:** An itemized list of the items to create; only the ones you confirm are created, and their keys go into
the dictionary.

## Usage

Ask in your own words ("WBS", "work breakdown structure", "break down the scope") or run
`/pm-skills:wbs-builder`.

## Inputs and outputs

- Reads `PROJECT.md`, `TAILORING.md`, `RACI.md`, the charter, roadmap, release plan and earlier WBS, and the issues
  tool through `TOOLS.md`.
- Writes one WBS in the folder of the project's Working documents section, named by `shared/scripts/doc_naming.py`,
  in the format of [`shared/documents/wbs.md`](../../shared/documents/wbs.md).
- On request, creates work items through an issues tool declared with Mode `write`, after you confirm the list.

## Requirements

A project register (`/pm-skills:project-setup`) is recommended, and a scope source is needed: a charter, a roadmap or a scope you describe.

## Limitations

- Stops at work packages: activities belong to the schedule, stories to the backlog.
- Does not change the RACI matrix or the schedule register; it tells you what they need.
- Scope not in the source is a change request, not an addition.
