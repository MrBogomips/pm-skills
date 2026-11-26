---
name: risk-register
description: Keeps the project's risk register (RISKS.md) - identifies threats and opportunities, assesses probability and impact, plans responses with owners and review dates, reviews and closes risks, flags the high ones. Use to set up, add to or review the risk register ("risk register", "risk log", "add a risk", "review the risks").
---

# Risk register

Keeps `RISKS.md`: the project's threats and opportunities, their assessment, the response chosen and who owns it.
It proposes; the user decides every risk, score and response written.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **Project register**: `PROJECT.md`, declared in the project's `AGENTS.md` (or `CLAUDE.md`) as
  `- Project register: \`<path>\``. The risk register is its `- Risk register: \`<path>\`` line under Registers.
  With no project register, suggest `/pm-skills:project-setup`; if the user wants to go on in the session, work on
  a path they name and invent no configuration.
- **Format**: `${CLAUDE_PLUGIN_ROOT}/shared/registers/risks.md`, the single source for columns, values and rules.
  Read it before writing; do not restate it to the user.
- **Tailoring**: the `## risk-register` section of the tailoring register, when declared.
- **Other registers, read only**: the decision log (`Decision log`), the team register (`Team register`) for owner
  slugs.
- **Tools** (from the tools register, by capability): `issues`, `incidents`, `code`, `ci`, `releases`. Without a
  tools register, say which sources could not be read.
- **Handoff proposals** from other skills, per `${CLAUDE_PLUGIN_ROOT}/shared/handoff.md`: input checked against
  this skill's rules, never an order. Accepting a proposal is not agreement to write: show the change and wait for it.
  For each entry written, report the IDs assigned to its proposer.

## Steps

1. **Start.** Read the project register, the risk register and the tailoring section. Say which tailoring rules
   apply. The high threshold is a score of at least 60% of the highest possible score (15 on a 1-5 scale), unless
   a `scale` rule sets it. If a `scale` rule sets a range other than the register's `Scale:` line, say so and
   propose aligning the line; never rescale existing assessments without the user re-assessing them.
2. **Set up** (no risk register, or the user asks):
   - propose `RISKS.md` at the project root (or where the Working documents section places registers), with the
     title, `Scale:` from the tailoring or `1-5`, and the header from the format;
   - propose the line `- Risk register: \`RISKS.md\`` for the Registers section of `PROJECT.md`;
   - show both, write after the user agrees, then validate `PROJECT.md` too:
     `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/project_register.py" validate <path>`.
3. **Identify.** From the user's words, or, when asked to look for risks, from the facts:
   - accepted decisions whose consequences carry uncertainty;
   - open issues that block or keep reopening, incidents in the last weeks, failing or flaky CI;
   - the software focus by name: technical debt, external dependencies and suppliers, upcoming releases and their
     readiness, single points of knowledge.

   With a lot to read, dispatch `project-activity-scout` in per-project mode (the path of `PROJECT.md`, a 42-day
   window) instead of reading the tools inline. Propose each candidate as cause, event and effect, with the fact it
   comes from; skip any already in the register. Write only the candidates the user accepts.
4. **Assess.** Propose Probability and Impact on the register's scale, with a one-line reason each; the user
   confirms. Score is Probability × Impact. Mark a risk at or above the high threshold as high.
5. **Plan the response.** Propose a Strategy allowed for the risk's Type, the Response actions, the Owner (a team
   register slug or a role, never a guess) and the Review date (sooner for high risks). Ask for what is missing.
6. **Write.** New risks get the next ID: the highest `R-` number in the file plus one, never a reused number;
   Raised is today. Show the rows, then write.
7. **Review** (the user asks, or risks are past their Review date):
   - list open and occurred risks past their Review date first, then high risks, then the rest;
   - for each, check the facts the tools give, propose a re-assessment, a new response or Review date, `occurred`
     (Response says how it is handled) or `closed` (Response says what happened);
   - a closed risk stays in the table; it is never deleted;
   - after a review of the whole register, set `Last reviewed` to today.
8. **Challenge** with `pm-critical-reviewer` when the user asks for a review of the responses, or when a high risk
   gets a new or changed response. Give it the facts only: the rows concerned, the scale and threshold, the related
   decisions and the facts the tools gave. Present its findings as proposals.
   **Fable escalation**: when the review prepares a risk response for a steering committee or a client, dispatch it
   with the model set to `fable`; tell the user before dispatching, and why.
9. **Escalate high risks.** List them for the user with the body they go to: from a `scale` or `rules` rule (for
   example the steering committee), otherwise ask. Strategy `escalate` is for a risk outside the project's
   authority. Offer a short message for the escalation; send it only through a `messages` tool with Mode `write`,
   after the user agrees; otherwise give it to the user to send.
10. **Validate** after every write:
    `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/risks_register.py" validate <path>` and fix until it exits 0.

## Always

- **Show before writing**: every change to `RISKS.md` or `PROJECT.md` is shown first and written after the user
  agrees.
- **One write per change**: the whole change in a single edit, so validation never sees a half-done state.
- **Facts apart from inferences**: say what was read, what was inferred and which sources were unavailable.
- **People as delivery facts**: a risk about people names a role or a delivery fact, never a judgment, a health
  matter or the reason for an absence; no contacts in any cell.
- Talk and write cell values in the user's language, or the project's `Deliverable language`; headings and column
  names stay in English.

## Never

- Never write the decision log, the team register or any external system except as stated in step 9.
- Never compute a score other than Probability × Impact, or fill an assessment the user has not confirmed.
- Never apply a tailoring rule that loosens a guardrail; say that it was ignored and why.

## Extension points

- `scale`: the Probability and Impact range, the high threshold and where high risks are escalated.
- `rules`: extra checks or approvals, for example who must agree to accept or close a high risk.
- `steps`: extra steps before writing a new risk or during a review.
- `terms`: the project's words for the register, categories and strategies in conversation.
