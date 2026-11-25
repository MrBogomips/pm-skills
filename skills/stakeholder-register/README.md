---
summary: For project managers - keeps STAKEHOLDERS.md, the register of stakeholders as roles and groups, with interest, influence and engagement levels you decide, the approach to each and its review date.
---

# stakeholder-register

Keeps `STAKEHOLDERS.md`, the project's stakeholder register. It finds stakeholders in the project's documents,
minutes and decision log, proposes their interest, influence and engagement with the facts behind each level, plans
what the project does where engagement falls short, and reviews the register when entries come due.

## Why

A stakeholder map drawn once at kick-off misses the operations team who must run the product and the sponsor who
stopped coming to reviews. This skill reads who decides, approves, requests changes and receives deliverables,
proposes each stakeholder with a reason you can check, and brings up entries past their review date. It writes roles
and levels, never opinions about people, because the register lives in a repository others read.

## Use cases

### Build the register from what the project already knows

**Context:** Acme Portal has a decision log and six months of meeting minutes, and no stakeholder register.

**Action:** Ask "identify the stakeholders".

**Result:** A list of candidate stakeholders as roles and groups (Sponsor, steering committee, end users, client IT
operations), each with the fact it comes from and proposed levels with reasons; the ones you accept are written with
an approach, an owner and a review date.

### Review the register before a release

**Context:** The session starts with "2 past review" for the stakeholder register.

**Action:** Ask "rivedi gli stakeholder".

**Result:** Overdue entries first, then influential stakeholders below their desired engagement, each with a
proposed change of level, approach or review date; once the whole register is reviewed, `Last reviewed` moves to
today.

### Keep a remark out of the file

**Context:** You describe the client's procurement lead as difficult.

**Action:** Ask to add them to the register.

**Result:** The entry is "Client procurement" with levels and an approach; the skill tells you the remark stays out
and why.

## Usage

Ask in your own words ("stakeholder register", "mappa degli stakeholder") or run `/pm-skills:stakeholder-register`.
Without a register the skill starts by setting one up and warns that the file may be shared.

## Inputs and outputs

- Reads `PROJECT.md` (declared in `AGENTS.md` or `CLAUDE.md`), the `stakeholder-register` section of
  `TAILORING.md`, the decision log, team register and change log, meeting minutes and project documents, and the
  project's tools by capability (documents, meetings) as listed in `TOOLS.md`.
- Writes `STAKEHOLDERS.md` in the format of
  [`shared/registers/stakeholders.md`](../../shared/registers/stakeholders.md), and once, with your consent, the
  `Stakeholder register` line in `PROJECT.md`.

## Requirements

A project register (`/pm-skills:project-setup`). The tools register is optional: without it the skill works from
the registers, the files in the project and what you tell it, and says which sources it could not read.

## Limitations

- Assessments are levels only; there is no free comment about a stakeholder.
- Names are optional and contacts are never stored: the register is not a contact list.
- Channels and cadence of communication are not planned here.
