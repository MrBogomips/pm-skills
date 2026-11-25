---
summary: For product owners and project managers - drafts and revises the product roadmap (Product Goal, themes, horizons) linked to epics and releases, keeping committed apart from intended.
---

# product-roadmap

Writes and keeps the product roadmap as a Markdown document: the Product Goal, the themes that serve it, and the
horizons (now, next, later, or dated ones) in which they are expected. Every item is tied to an epic in the issues
tool or a release, and marked committed or intended by its source.

## Why

Roadmaps lose trust when intentions read like promises and dates appear that nobody committed to. This skill builds
the roadmap from the facts (epics, releases, decisions, approved changes) and labels each item by where its
commitment comes from. It revises the same document in place with a new version and records what moved and why, so
stakeholders can follow how the plan changed.

## Use cases

### Draft the first roadmap

**Context:** A new product with epics in the issues tool and a first release planned.

**Action:** Ask "draft the product roadmap".

**Result:** The skill asks for the Product Goal and the themes, proposes now, next and later from the epics, marks
the release items as committed, and shows the draft before writing it.

### Revise the roadmap after a change request

**Context:** A change request was approved and a theme moved to the next quarter.

**Action:** Ask "update the roadmap".

**Result:** A revision with a minor version bump, "Changes from the previous version" listing what moved and the
change request behind it, and the same file updated after you agree.

### Answer "when will it be done?"

**Context:** A stakeholder asks for a date for a theme in "Later".

**Action:** Ask "put a date on the reporting theme".

**Result:** The skill keeps the date out unless the project committed one, and points to a forecast from
throughput, which is a separate job.

## Usage

Ask in your own words ("product roadmap", "update the roadmap", "now/next/later") or run
`/pm-skills:product-roadmap`.

## Inputs and outputs

- Reads `PROJECT.md` (declared in `AGENTS.md` or `CLAUDE.md`), the `product-roadmap` section of `TAILORING.md`, the
  decision log, the change log and the risk register, epics through the issues capability, releases and milestones
  through the releases and schedule capabilities in `TOOLS.md`, and the previous roadmap.
- Writes the roadmap in the format of
  [`shared/documents/product-roadmap.md`](../../shared/documents/product-roadmap.md), named and versioned by the
  project's conventions, where the Working documents section places documents.

## Requirements

A project register (`/pm-skills:project-setup`). The tools register is optional: without it, the roadmap is drafted
from what you tell it and says which sources it could not read.

## Limitations

- It does not forecast dates; a date appears only when the project committed it.
- The Product Goal, the themes and the order are yours to set; the skill proposes wording from the facts.
- It does not change epics or releases in the tools.
