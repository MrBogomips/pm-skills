---
summary: For project managers - keeps RACI.md, the responsibility matrix by role, with exactly one accountable role per deliverable, built from the WBS or the charter and checked against the team and stakeholder registers.
---

# raci-matrix

Keeps the project's RACI matrix: for each deliverable or activity, which role is responsible, accountable, consulted
and informed. Columns are roles, so the matrix survives people joining and leaving; the team register says who holds
each role.

## Why

A responsibility matrix goes wrong in two ways: two people think they own the same deliverable, or nobody does, and
it goes stale as soon as someone leaves. This skill keeps one accountable role per row, enforced by a validator that
runs after every edit, and uses roles instead of names. It also tells you when a role or a work package in the matrix
no longer exists in the other registers.

## Use cases

### Build the matrix from the WBS

**Context:** Acme Portal has an issued WBS and a team register with Product owner, Tech lead and Developers.

**Action:** Ask "build the RACI matrix".

**Result:** One row per work package with its WBS ID, columns for the team roles plus the Sponsor and the Security
office from the stakeholder register, one proposed `A` per row with its reason; written after you confirm.

### Ask who is accountable

**Context:** The go-live runbook is late and you need to know who answers for it.

**Action:** Ask "chi è responsabile del runbook?".

**Result:** The accountable role from the matrix and who is responsible for the work; the person holding the role
only if you ask.

## Usage

Ask in your own words ("RACI", "responsibility matrix", "matrice RACI") or run `/pm-skills:raci-matrix`.

## Inputs and outputs

- Reads `PROJECT.md`, `TAILORING.md`, `TEAMS.md` (roles only), `STAKEHOLDERS.md`, the latest WBS and project
  charter.
- Writes `RACI.md` in the format of [`shared/registers/raci.md`](../../shared/registers/raci.md), validated by
  `shared/scripts/raci_register.py`; the plugin's hooks validate it after every edit.

## Requirements

A project register (`/pm-skills:project-setup`). A team register helps; without one the skill asks for the roles.

## Limitations

- Holds roles, never people; mapping a role to a person is the team register's job.
- Does not check role names against the other registers in the validator: the skill reports mismatches when you
  run it.
- Does not change the WBS or the registers it reads.
