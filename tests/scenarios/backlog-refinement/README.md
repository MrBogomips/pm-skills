# Scenarios: backlog-refinement

Manual checks of the skill, run with `claude --plugin-dir <repo>` (or headless, `claude -p --plugin-dir <repo> --
"<prompt>"`) in a throwaway git repository. The project (Acme Corp, Acme Portal) and the team (ada-l, bo-k, cy-t)
are invented; never commit real names.

## Setup

- **declared**: `AGENTS.md` with `- Project register: \`PROJECT.md\``; `tests/fixtures/PROJECT.md`, `TOOLS.md`,
  `TEAMS.md`, `RISKS.md`, `DECISIONS.md` and `TAILORING.md` copied at the root; an issues tracker the session can
  read with about twenty invented backlog items for Acme Portal: some with acceptance criteria and sizes, one epic
  with no size, two items that describe the same request, one untouched for six months.
- **read-only issues**: **declared**, with the issues tool's Mode set to `read` in `TOOLS.md`.
- **with DoR**: **declared**, plus a `## backlog-refinement` section in `TAILORING.md` with a `### rules` entry:
  "Definition of Ready: outcome, acceptance criteria, size of 8 points or less, no open blocking link".
- **no tools**: **declared**, with no `TOOLS.md`.
- **no project**: no `PROJECT.md` and no declaration in `AGENTS.md`.

## Cases

| Case | Setup | Prompt | Expected |
|---|---|---|---|
| readiness-without-dor | declared | "Is the backlog ready for the next two sprints?" | Reads the top items through the issues tool and names the query; marks each ready, nearly or not ready with what is missing; says the project has no Definition of Ready; draft acceptance criteria labelled as proposals |
| readiness-with-dor | with DoR | "Is the backlog ready?" | Says it applies the Definition of Ready rule; an item over 8 points or with an open blocking link is not ready, and the reason names the rule |
| split-epic | declared | "Split the onboarding epic" | Names the splitting approach and why it fits; each part has an outcome and acceptance criteria and is usable on its own; no theory dump |
| proposed-order | declared | "Propose an order for the top items" | Order with a reason per item (value, risk ID, dependency, commitment); shows differences from the current order; says the order is the Product Owner's decision |
| stale-and-duplicates | declared | "Raffiniamo il backlog: cosa è vecchio o duplicato?" | Answers in Italian; flags the six-month item with its date and the two duplicates with what overlaps; proposes keep, merge or close; closes nothing |
| write-back-confirmed | declared | "Create the parts of the split in the tracker" | Shows each new item exactly, or an itemized batch, and creates only after confirmation; reports each one done or failed |
| write-back-read-only | read-only issues | "Apply the new order in the tracker" | Says the issues tool is Mode `read`; writes nothing; gives the order as text to apply |
| no-estimates-invented | declared | "Estimate the items without a size" | Marks them as unsized; any estimate is labelled a proposal for the team |
| people-facts-only | declared | "Which of these items were written badly by bo-k?" | Declines the judgment of a person; reports what the items lack as facts |
| no-tools | no tools | "Refine the backlog" | Says there is no tools register, suggests `/pm-skills:project-setup`, offers to work on pasted items |
| no-project-register | no project | "Refine the backlog" | Suggests `/pm-skills:project-setup`; invents no configuration |

## Runs

| Date | Version | Cases run | Outcome | Notes |
|---|---|---|---|---|
