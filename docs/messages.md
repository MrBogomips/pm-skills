---
title: Messages people can act on
area: stakeholders
type: operational
---

# Messages people can act on

A request that leaves the reader guessing who, what or by when waits until someone chases it. `actionable-message`
writes an email or a chat message, or rewrites your draft, so that the people who receive it can act without asking
back. The message stays in the conversation as a Markdown draft; it is copied or sent only after you approve it.

Ask in your own words, naming the message: "write an email asking Ada to review the go-live runbook by 2026-11-30,
per D-002", "make the message in drafts/runbook-mail.md actionable", "send a reminder to Bo".

## The five elements

Every request in the message names:

| Element | What it holds |
|---|---|
| Owner | one person by name, or a role or group when that is what you mean, from the team register, the RACI matrix or the stakeholder register |
| Ask | the action, and what "done" looks like: what is delivered, decided or answered |
| Deadline | an absolute date, never "soon" or "Friday" |
| References | what the owner needs to act: issue keys, pull requests, `D-NNN`, `CR-NNN`, `R-NNN`, documents |
| Contact | whom the owner asks when in doubt, by name and role, with the channel |

When an element cannot be read from your request or the registers, the skill proposes one from the registers and
asks you to confirm it; it never fills a gap with a guess. It warns you when the capacity register shows the owner
away before the deadline, without the reason. A message that only informs has no owner and no deadline, but keeps
its references and contact.

## Two formats

| Format | Shape | Chosen for |
|---|---|---|
| `friendly` | two to five sentences of prose in a colleague's tone, no headings, labels, lists or tables; the request in the first or second sentence | a colleague on the team, one request or a short, simple content |
| `strong` | a greeting, a **Requests** section, a **Context** section and a closing with the contact | several owners, a client, a steering committee or a formal reminder |

In `strong`, one or two requests become one block per owner with the labeled fields Who, What, Done when, By,
References and Contact. Three or more become a table with the columns Who, What (the "done when" in italic after
it), By and References, and the contact once below it.

The skill says which format it chose and why, in one line. A client gets a formal register in either format. In
`friendly`, the contact may be left implied when it is the sender.

## Options

Options go after the skill name as arguments, or in your words ("make it strong", "no formatting"):

| Option | Effect |
|---|---|
| `strong`, `friendly` | the format, whatever the audience |
| `+emoji` | marker emoji at the start of section titles and labels (strong) or at most one at the end of a sentence (friendly); never in a formal message to a client |
| `-formatting` | no emphasis: in strong, section titles stay and the labels become plain lines, with no bold, italic, table or list markers; friendly loses its bold; links stay links in both |

```text
/pm-skills:actionable-message strong +emoji remind Ada, Bo and Cy of their go-live tasks for 2026-12-05
/pm-skills:actionable-message friendly ask Bo to book the rollback window by 2026-12-01
```

An option you give wins over a `format` rule in `TAILORING.md`, and that rule wins over the choice by audience.

## Emphasis and links

- **Bold** marks the owner, the deadline and the action (verb and object), at most once per sentence, field or
  cell, never a whole sentence. In `friendly`, only the deadline and the action are bold, and both may be in the
  request sentence.
- **Italic** marks the "done" condition, a caveat or a quoted term.
- No capitals and no underline for emphasis.

Every reference with a URL is a link, written as `<key> · <short title>`, for example
[ACME-142 · Go-live runbook](https://example.com/acme/pull/142); a pull request with no issue key is linked as
`#<number> · <title>`. The URL comes from the `issues` or `code` tool declared in `TOOLS.md`, or from you; the
skill never composes one by guess. A reference with no URL in reach, such as a register ID like `D-002`, stays
plain text, and the skill names it in its report.

## Pasting into an email client

Ask "give it to me for Outlook" (or Mail). Once you approve the draft, the plugin renders it for the email client:
you get a page in the temporary folder, never in the project, to open in the browser and copy from, and the subject
and the recipients apart, as plain text, to fill in the client's own fields. If you prefer the clipboard, ask for it.

Pasted into Outlook on the web, Outlook for Mac or Mail, these survive: tables, bold, italic, links, one-level
lists and emoji. The font is the client's: it applies its own to the pasted message.

## Slack and plain text

There are two cases:

- **Sent through a declared tool.** When `TOOLS.md` declares a tool with Purpose `messages`, Mode `write` and a Scope
  that covers the destination, the skill shows exactly what goes where (channel or recipients, subject, text) and
  sends after you confirm. A Slack tool gets the `slack` rendering, with Slack's own bold, italic and links; another
  chat tool gets what its description says it accepts, `plain` when in doubt; an email tool gets HTML when it takes
  it, else `plain`.
- **Pasted by hand** into Slack, Teams or another chat. You get the `plain` rendering in the conversation, not the
  `slack` one, which goes only through a declared tool: links stay full URLs, which chats turn into links, and the
  emphasis is lost.

With no declared tool the skill hands the message over and says it was not sent.

## What a project can fix in `TAILORING.md`

Rules go under a `## actionable-message` section, by extension point:

| Extension point | Examples |
|---|---|
| `format` | the default format per audience ("strong for anything to Acme Corp"), emoji on or off, a fixed subject prefix, a signature block |
| `rules` | who is always in Cc for messages to the client, a minimum notice before a deadline |
| `steps` | extra steps before drafting or before sending |
| `terms` | the project's words for requests, owners and channels |

The skill says which rules it applied. See [Registers and their keepers](registers-and-keepers.md) for the tailoring
register and `/pm-skills:pm-tailoring` to change it.

## What the skill never does

- Send without your confirmation, or through a tool not declared `write`.
- Write to the clipboard unless you ask, or before you approve the draft.
- Write an email address or phone number into a register or a project file: an address appears in the message only
  when you give it in the session.
- Edit a register: for someone the registers do not know, it proposes a handoff to `team-register` or
  `stakeholder-register`.
