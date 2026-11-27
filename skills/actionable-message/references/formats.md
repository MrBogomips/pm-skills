# Message formats

Read when drafting. The draft is Markdown limited to the subset that
`${CLAUDE_PLUGIN_ROOT}/shared/scripts/message_render.py` accepts: `#` and `##` headings, paragraphs, one-level `- `
and `1. ` lists, pipe tables, `**bold**`, `*italic*` and `[text](url)` with `http`, `https` or `mailto` only.
Anything else (nested lists, quotes, code, images, underline, HTML) is out: the script prints it as literal text.
It stops with exit 1 only for a link that is not `http`, `https` or `mailto`, a table row whose cells do not match
the header, or an empty message. Consecutive lines are joined into one paragraph, a sign-off too: a blank line separates paragraphs. Subject and
recipients stay outside the draft.

## Choosing the format

An option the user gives, as an argument or in words, wins; then a `format` rule in `TAILORING.md`; then:

- **friendly** for a colleague on the team, with one request or a short, simple content;
- **strong** for several owners, a client, a steering committee or a formal reminder.

Say which format was chosen and why, in one line. The options: `+emoji` (below) and `-formatting`, which drops the emphasis in both formats: strong as below,
friendly with no bold. References with a URL stay links in both.

## Strong

Greeting; section **Requests**; section **Context**; closing with the contact.

- **One or two requests**: one block per owner, a list with the labeled fields *Who*, *What*, *Done when*, *By*,
  *References*, *Contact*, in this order. The labels are plain text; the values carry the emphasis below.
- **Three or more**: a table with the columns Who, What (with "done when" in italic after it), By, References, and
  the contact once below it.
- **`-formatting`**: the same sections and labels as plain lines, with no bold, italic, table or list markers; each
  field is a paragraph of its own, so separate the lines with blank lines. Links stay links.

## Friendly

Two to five sentences of prose in the tone of a colleague: no headings, labels, lists or tables. The request comes in
the first or second sentence. All five elements are present inside the sentences; the contact may be left implied
when it is the sender.

## Emphasis

- **Bold**: the owner, the deadline, the action (verb and object).
- **Italic**: the "done" condition, a caveat, a quoted term.
- At most one bold per sentence (in a list or table, per field or cell); never a whole sentence; no capitals, no
  underline. In the context, only the key fact of a paragraph.
- **Friendly**: bold only, on the deadline and the action.

## Emoji

Off by default; on with `+emoji` or a `format` rule; never in a formal message to a client. Markers only, at the
start of a section title or a label, at most one each: 📌 requests, 📅 deadline, 🔗 references, ℹ️ context,
💬 contact. Friendly: at most one, at the end of a sentence.

## Links

Every reference with a URL is a link, in both formats: `[<key> · <short title>](<url>)`, where the key is the issue
key, or `#<number>` for a pull request that has none. The URL comes from the `issues` or `code` tool or from the user,
never composed by guess. A reference with no URL in reach (a register ID such as `D-002`, a key that could not be
checked) stays plain text and is named in the report.

## Channels

The draft is the same Markdown whatever the destination; `SKILL.md`, step 8, renders it for the channel. A chat
pasted by hand gets the `plain` rendering: emphasis is lost there, links stay full URLs.

## Examples

### Strong, two owners

```markdown
Hi Ada, hi Bo,

## Requests

- Who: **Ada L.**, tech lead
- What: **review the go-live runbook**
- Done when: *your comments are in the pull request and you have approved it or sent it back*
- By: **Monday 30 November 2026**
- References: [ACME-142 · Go-live runbook](https://example.com/acme/pull/142), D-002
- Contact: Cy M., project manager, on #acme-golive

- Who: **Bo K.**, operations
- What: **book the rollback window** with the hosting provider
- Done when: *the window is confirmed in writing and added to the release calendar*
- By: **Tuesday 1 December 2026**
- References: [ACME-150 · Rollback window](https://example.com/acme/issues/150)
- Contact: Cy M., project manager, on #acme-golive

## Context

Decision D-002 moved the go-live to **Saturday 5 December 2026**. The runbook must be approved before the rollback
window can be booked.

Write to me on #acme-golive for anything. Thanks, Cy
```

### Strong, three owners, with `+emoji`

```markdown
Hi all,

## 📌 Requests

| Who | What | By | References |
|---|---|---|---|
| **Ada L.** | **Review the go-live runbook** — *done when it is approved or sent back in the pull request* | **30 Nov 2026** | [ACME-142 · Go-live runbook](https://example.com/acme/pull/142) |
| **Bo K.** | **Book the rollback window** — *done when it is confirmed in writing* | **1 Dec 2026** | [ACME-150 · Rollback window](https://example.com/acme/issues/150) |
| **Cy M.** | **Send the go-live notice** to the client — *done when the client has acknowledged it* | **2 Dec 2026** | D-002 |

💬 Contact for all three: Ada L., tech lead, on #acme-golive.

## ℹ️ Context

The go-live moved to **Saturday 5 December 2026** (D-002); each step needs the one before it.

Thanks, Ada
```

### Friendly

```markdown
Hi Bo, could you **book the rollback window** with the hosting provider? I need it confirmed in writing and in the
release calendar by **Tuesday 1 December 2026**, since the go-live moved to 5 December (D-002). The details are in
[ACME-150 · Rollback window](https://example.com/acme/issues/150). Ping me with any question.
```
