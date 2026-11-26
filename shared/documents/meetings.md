# Meetings: what the brief and the minutes share

The meeting brief (`shared/documents/meeting-brief.md`) prepares a meeting; the minutes
(`shared/documents/meeting-minutes.md`) record it. Both point here for what they have in common. The common rules
(frontmatter, naming, versioning) are in `shared/documents/common.md`.

## Kinds of meeting

The `meeting` key holds the kind or the title of the meeting. The kinds the plugin knows, so that skills can look
for the previous meeting of the same kind and for its row in the communication plan's Meetings table:

| Kind | Typical purpose |
|---|---|
| `steering committee` | decisions and escalations at sponsor level |
| `client meeting` | alignment, acceptance, change requests with the customer |
| `kick-off` | starting a project, a phase or a release |
| `status meeting` | regular progress and risks with the team or the stakeholders |
| `sprint review`, `retrospective` | covered by their own skills; their record is not meeting minutes |
| `other` | any meeting the user names |

A kind is a label, not a closed list: the project's `format` extension of the skills may add kinds.

## Frontmatter keys

The two documents add these keys to the common ones:

| Key | Rule |
|---|---|
| `meeting` | the kind or title (`steering committee`, `kick-off with Acme Corp`) |
| `attendees` | brief: the people or roles invited; minutes: the ones present. Comma-separated, work names or roles only, no contacts |

`date` is the day of the meeting. The minutes add `brief:` (see below).

## Agenda item

An agenda item has the same four parts in both documents:

| Part | Rule |
|---|---|
| Item | what is discussed, in a few words |
| Time | minutes allotted (brief) or as discussed (minutes) |
| Owner | who leads the item: a role or a team register slug |
| Decision sought | what the meeting is asked to decide or agree on; `information only` when nothing |

## How the brief and the minutes link

- The brief is written first. The minutes inherit its agenda and attendees and record in `brief:` the path of the
  brief, relative to the project root.
- The minutes' Agenda lists the brief's items, adjusted to what was actually discussed; the brief is not edited
  afterwards.
- Items the brief brings in carry their register IDs (`AC-012`, `D-003`, `R-004`, `CR-002`, `G-001`); the minutes use
  the same IDs when they report what happened to them.
- Without a brief, the minutes stand alone, as before.

## Rules

- Work names and roles only: no email addresses, phone numbers or other contacts, no sensitive personal data, no
  evaluation of people.
- A register entry is written only by its keeper (`shared/handoff.md`); a meeting document links to the entry by ID.
