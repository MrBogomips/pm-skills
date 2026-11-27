---
summary: For project managers - writes or rewrites emails and chat messages where every request has an owner, an ask, a deadline, references and a contact; sends only on your confirmation.
---

# actionable-message

Writes an email or a chat message, or rewrites your draft, so that the people who receive it can act without asking
back. Each request names its owner, what is asked and what "done" means, the deadline, the references to act on and
whom to contact with questions. It sends the message only when you ask and confirm.

## Why

Messages like "can someone look at the runbook soon?" leave the reader guessing who, what and by when, and the work
waits until someone chases it. This skill resolves owners from the team register, the RACI matrix and the stakeholder
register, turns "soon" into a date you choose, cites decisions, changes, risks and work items by their IDs and checks
that they exist, and warns you when the capacity register shows the owner away before the deadline. It asks for what
is missing instead of inventing it, and lists what it inferred for you to correct.

## Use cases

### Ask for a review with a deadline

**Context:** The go-live runbook needs a review after decision D-002.

**Action:** Ask "write a message asking Ada to review the go-live runbook by 2026-11-30, per D-002".

**Result:** A message with the request first: Ada as owner, what the review must produce, the date, D-002 as
reference, a placeholder for the contact and the runbook link it could not find; Cc proposed from the RACI matrix for
you to confirm, and a note that Ada is away from the next day.

### Make your own draft actionable

**Context:** You wrote "we need to sort out the runbook soon, can someone look at it?".

**Action:** Ask "make the message in drafts/runbook-mail.md actionable".

**Result:** The same message in your voice, one block per owner proposed from the RACI matrix, and questions for the
dates, the names and the contact.

### Send it on the team channel

**Context:** The project declares a chat tool with Purpose `messages`, Mode `write` and the team channel in its Scope.

**Action:** Ask to write the message and send it on the channel.

**Result:** The channel, recipients and text shown first; the message is sent only after you confirm.

## Usage

Ask in your own words ("write an email asking", "follow-up message", "send a reminder") or run the
skill with what you want, or with a draft pasted or given as a file:

```text
/pm-skills:actionable-message write a message asking Ada to review the go-live runbook by 2026-11-30, per D-002
```

The skill picks a format: `friendly`, a few sentences of prose for a colleague with one simple request, or `strong`,
with Requests and Context sections, for several owners, a client or a formal reminder. You can choose it, add emoji
markers with `+emoji`, or drop bold, italic, lists and tables with `-formatting`:

```text
/pm-skills:actionable-message strong +emoji remind Ada, Bo and Cy of their go-live tasks for 2026-12-05
/pm-skills:actionable-message friendly ask Bo to book the rollback window by 2026-12-01
```

A project can set the default format per audience, and turn emoji on, with a `format` rule in `TAILORING.md`.

## Inputs and outputs

- Reads `PROJECT.md` and the registers it declares (team, RACI, stakeholders, capacity, decisions, changes, risks,
  tailoring); checks work item and pull request references through the `issues` and `code` tools.
- Writes no project file: the message is a Markdown draft in the conversation, with references as links. Saved on
  request where you say; a copy inside the project leaves out any address you gave.
- Once you approve the draft, renders it: HTML on the clipboard for an email client (Outlook, Mail), plain text for
  a chat pasted by hand. With no clipboard, an HTML file in the temporary folder, to open in a browser and copy.
- Sends only through a tool declared with Purpose `messages` and Mode `write`, after you confirm.

## Requirements

A project register (`/pm-skills:project-setup`) is recommended; without it the skill asks for owners, references and
contacts. The team register and the RACI matrix make owners and Cc proposals possible; the capacity register makes
the warning on absences possible.

Python 3 renders the message. Copying to the clipboard uses `osascript` and `pbcopy` on macOS (built in), or
`xclip` or `wl-copy` on Linux; nothing else needs them.

## Limitations

- Writes one message at a time; it may hold several requests for several owners.
- Does not keep contacts: an address appears in the message only when you give it.
- Does not edit any register: for someone the registers do not know, it proposes a handoff to `/pm-skills:team-register` or
  `/pm-skills:stakeholder-register`.
- Does not track replies: write a reminder with the skill when you need one.
- Does not send documents: to distribute a report or minutes, use `/pm-skills:publish-deliverable`.
- The email client applies its own font to the pasted message; lists are one level only, never nested.
- On Linux the rich copy carries no plain-text twin: an application that only takes plain text gets nothing to paste.
- In a chat pasted by hand, bold and italic are lost; links stay full URLs.
