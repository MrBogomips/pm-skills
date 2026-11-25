---
summary: For teams and their project managers or Scrum Masters - prepares a team charter workshop with a draft from the project files and the questions only the team can answer, then records the agreements the team made, never about individuals.
---

# team-charter

Prepares and records the team charter: the team's purpose, values and working agreements on communication, meetings
and hours, decisions, reviews and quality, tools, and how disagreements are handled.

## Why

A team charter is worth something only if the team writes it; a template filled in by one person is ignored. This
skill does the preparation (what the project already settles, agreements the team made in retrospectives) and leaves
the decisions to the workshop as open questions. After the workshop it records the agreements as the team made them,
with no names attached, and leaves unanswered questions open instead of inventing answers.

## Use cases

### Prepare the workshop

**Context:** Acme Portal's team grew from three to six people and wants to restate how it works.

**Action:** Ask "prepare the team charter workshop".

**Result:** A draft with the purpose from the project charter, the Definition of Done linked, two agreements taken
from recent retrospectives, and the open questions under each heading.

### Record the outcome

**Context:** After the workshop you paste the notes from the board.

**Action:** Ask "registra la carta del team".

**Result:** The agreements rephrased as what the team does, values with their practical meaning, names and votes
removed, the questions still open listed for you, and a review date.

## Usage

Ask in your own words ("team charter", "working agreements", "carta del team") or run `/pm-skills:team-charter`. Say
whether you are preparing or recording; the skill asks if it cannot tell.

## Inputs and outputs

- Reads `PROJECT.md`, `TAILORING.md`, `TEAMS.md` (roles only), the project charter, the earlier team charter, recent
  retrospectives, and the meetings tool through `TOOLS.md`.
- Writes one team charter in the folder of the project's Working documents section, named by
  `shared/scripts/doc_naming.py`, in the format of
  [`shared/documents/team-charter.md`](../../shared/documents/team-charter.md).

## Requirements

A project register (`/pm-skills:project-setup`).

## Limitations

- Does not run the workshop; it prepares it and records its outcome.
- Never records who said what, and never writes personal circumstances, even as the reason for a working-hours
  agreement.
