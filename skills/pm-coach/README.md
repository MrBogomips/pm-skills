---
summary: For project managers - a coach that reads your project's registers, asks a few questions and gives reasoned advice, a straight answer or Socratic questions, and points to the skill that does the next step.
---

# pm-coach

A coach for the project manager: describe a situation on your project and get advice grounded in its registers,
in the style you ask for. It reads, reasons and suggests; it never writes anything.

## Why

Project management advice is easy to find and hard to fit: the right move depends on the delivery approach, the
contract, the risks already known and the decisions already taken. This skill reads them from `PROJECT.md` and the
registers before advising, says which facts it used and which were missing, names the guide behind the advice (PMBOK
Guide, Eighth Edition; Scrum Guide 2020; Kanban Guide v2025.5) and tells you which skill of the plugin does the next
step. Because it never writes, you can think out loud with it without changing the project.

## Use cases

### Decide how to handle a slipping milestone

**Context:** A fixed-price Acme Portal release is two weeks late and the client asks for a new date.

**Action:** Run `/pm-skills:pm-coach` and describe the situation.

**Result:** Two or three questions (what is driving the delay, what the contract allows, who decides), then a
recommendation with the options weighed, the risks from `RISKS.md` it relied on, and a suggestion to record the
outcome with `/pm-skills:decision-log` and update `/pm-skills:risk-register`.

### Get a straight answer

**Context:** You need to know whether to raise a dependency risk at tomorrow's steering committee.

**Action:** "Just tell me: do I escalate it?"

**Result:** A direct recommendation in a few lines with its main assumption.

### Think a problem through

**Context:** A Scrum team keeps missing its Sprint Goal and you want to understand why before acting.

**Action:** "Let me think it through."

**Result:** One or two questions at a time, building on your answers, with no recommendation until you ask for one;
the coach names who holds each Scrum accountability rather than assigning one to you.

## Usage

Run `/pm-skills:pm-coach` with the situation in your own words ("how should I handle...", "advise me as a PM").
Say "just tell me" or "let me think it through" to change the style at any time. The skill starts only when you
call it.

## Inputs and outputs

- Reads the project register declared as `` - Project register: `PROJECT.md` `` in `AGENTS.md` (or `CLAUDE.md`), the
  registers it lists that bear on the question, the Definition of Done or of Workflow when relevant, and the files you
  name. Formats are in [`shared/registers/`](../../shared/registers/).
- Reads its own section of `TAILORING.md`: `rules` (governance the advice must respect) and `terms` (the project's
  vocabulary).
- Outputs advice in the conversation only. Writes no file and nothing to external systems.

## Requirements

None beyond the plugin. Without a project register it says so, suggests `/pm-skills:project-setup` and coaches on
what you tell it.

## Limitations

- Does not query external tools (issues, code, schedule): it reasons on the project files and on what you say.
- Does not run other skills or agents; it names them for you to run.
- Gives no appraisal of people and no human resources advice: about people it reasons on delivery facts only.
- Dates, costs and forecasts come from the registers or the plugin's skills, not from its own arithmetic.
