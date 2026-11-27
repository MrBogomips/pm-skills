---
name: actionable-message
description: Writes or rewrites an email or chat message so every request names its owner, the ask, the deadline, the references and a contact, in a strong or friendly format, rendered for Outlook or a chat; sends only on confirmation through a declared tool. Use for "write an email asking", "send a reminder", "make this message actionable", "format this message for Outlook"; not to send a document.
argument-hint: "[strong|friendly] [+emoji] [-formatting] <what to ask, or a draft>"
---

# Actionable message

Turns what the user wants from people into a message they can act on without asking back: who does what, by when,
with which references and whom to ask. It is sent only when the user says so.

**Italian.** If the user writes in Italian or the `Deliverable language` is Italian, first read
`${CLAUDE_PLUGIN_ROOT}/shared/glossary/it.md` and use its terms; the project's `terms` come first.

## Inputs

- **The intent**: what the user wants, in their words, or a draft to rewrite (pasted, or a file).
- **The project register**: `PROJECT.md`, declared by `` - Project register: `PROJECT.md` `` in the project's
  `AGENTS.md` (or `CLAUDE.md`): `Project name`, `Deliverable language` and the Registers. With no project register,
  name `/pm-skills:project-setup` in your answer, then write the message from what the user gave, asking for what
  you would have read there.
- **Registers, read only, when declared**: the team register (names, roles, work accounts), the RACI matrix (who is
  responsible, accountable, consulted, informed), the stakeholder register (roles and organizations outside the
  team), the capacity register (who is away before a deadline), the decision log, the change log and the risk
  register (IDs to cite as references), the tailoring register.
- **Tools register**: `issues` and `code` tools, to check the links and keys cited; a `messages` tool in Mode
  `write` to send it. Format: `${CLAUDE_PLUGIN_ROOT}/shared/registers/tools.md`.
- **Formats**: `${CLAUDE_PLUGIN_ROOT}/skills/actionable-message/references/formats.md`, read before drafting: the
  `strong` and `friendly` formats, options, emphasis, links, examples.

## Steps

1. **Read the configuration** and the `## actionable-message` section of `TAILORING.md`; say which rules apply.
2. **Find the requests.** Split the intent into requests and information. For each request, establish:
   - **Owner**: one person by name, or a role or group when that is what the user means; resolved from the team
     register, the RACI matrix or the stakeholder register;
   - **Ask**: the action, and what "done" looks like (what is delivered, decided or answered);
   - **Deadline**: an absolute date, never "soon" or "Friday";
   - **References**: what the owner needs to act: issue keys, pull requests, `D-NNN`, `CR-NNN`, `R-NNN`, documents;
   - **Contact**: whom the owner asks when in doubt, by name and role, with the channel.

   The reason is optional. Information that asks nothing of anyone has no owner and no deadline, but keeps its
   references and contact.
3. **Ask for what is missing.** When an owner, an ask, a deadline or a contact cannot be read from the intent or the
   registers, propose one from the registers (the `R` or `A` role in the RACI matrix for a deliverable) and ask the user
   to confirm it. When the capacity register shows the owner away or at 0% allocation before the deadline, say so, with
   no reason, and ask whether to move the date or the owner.
4. **Check the references** you can reach: keys and IDs exist in the registers or tools; say which you could not
   check.
5. **Draft one message**, however many requests and owners it holds, in the language of the request, else the
   `Deliverable language`, in a register that fits the audience (formal for a client). Choose the format and options
   as the formats reference says; draft in Markdown within its subset:
   - the subject (for an email) names the action and the date;
   - recipients: To the owners; Cc proposed from the RACI matrix (accountable and informed roles for the
     deliverables concerned), for the user to confirm.

   When rewriting a draft, keep the user's voice and register; change what makes a request unclear.
6. **People not in the registers.** When the message names someone in no register, list them with the role and
   organization the user gave, and suggest `/pm-skills:team-register` for a team member or
   `/pm-skills:stakeholder-register` for someone outside the team. A handoff to the keeper
   (`${CLAUDE_PLUGIN_ROOT}/shared/handoff.md`) is proposed, and handed over only when the user agrees.
7. **Show the message**: the Markdown draft with its recipients, the format and options chosen and why in one line,
   the references left without a link and what you inferred, for the user to approve.
8. **Hand over or send, only on request** and after the user approves the draft. Render it with `python3
   "${CLAUDE_PLUGIN_ROOT}/shared/scripts/message_render.py" --to html|plain|slack [--out FILE] <<'EOF'`, the draft in
   the quoted heredoc, so `$` and backticks stay literal: `html` for an email client, `plain` for a chat pasted by
   hand, `slack` only to send through a Slack tool.
   - To send, take the rendering the tool accepts (`plain` when in doubt) from stdout to a tool with Purpose
     `messages`, Mode `write` and a Scope that covers the destination; show exactly what goes where (channel or
     recipients, subject, text) and send after the user confirms. With no such tool, hand over and say it was not sent.
   - By hand, hand the rendering over the way the user asks; by default `html` with `--out` to a file in the temporary
     folder, never in the project, to open in a browser and copy from, and `plain` printed in the conversation; subject
     and recipients apart, as plain text. Copy it to the clipboard only when the user asks.
   - Exit 1 (a link not `http`, `https` or `mailto`, a table row not matching its header, an empty draft; stderr names
     the line): fix it and show the draft again before rendering. Exit 2 (usage or file error): fix the command.
   - Save the message to a file only when the user asks, where the user says; a copy saved inside the project keeps
     names, roles and channels, and leaves out the addresses the user gave, saying so.
9. **Report** what you read, what you inferred and what you could not read or check.

## Always

- Every request names its owner, the ask with what "done" means, the deadline, the references and a contact.
- Name people as the team calls them; cite registers by ID.
- Show before sending; send only after the user confirms.
- Every reference with a URL is a clickable link.

## Never

- Never invent an owner, an ask or its "done" condition, a deadline, a reference or a contact.
- Never write an email address, phone number or other personal contact into a register or any file in the
  project; in the message, use only addresses the user gives in the session.
- Never mention the reason for someone's absence, or judge a person, in the message.
- Never edit a register: suggest the skill that owns it.
- Never send through a tool that is not declared `write`, or without the user's confirmation.
- Never build a URL by guess.
- Never write the rendered message inside the project.

## Extension points

- `format`: the default format per audience, emoji on or off, a fixed subject prefix or a signature block.
- `rules`: extra checks, such as who is always in Cc for messages to the client, or a minimum notice before a
  deadline.
- `steps`: extra steps before drafting or before sending.
- `terms`: the project's words for requests, owners and channels.
