#!/usr/bin/env python3
"""Parse and validate an action log (ACTIONS.md).

The format is specified in shared/registers/actions.md. Python 3 standard library only.

Usage:
    actions_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# Actions"
HEADING_RE = re.compile(r"^## (AC-[0-9]{3,})\s+(\S.*)$")
REQUIRED = ("Raised", "Owner", "Status", "Action", "Source")
OPTIONAL = ("Due", "Raised by", "Tool", "Item", "Closed", "Outcome")
KEYS = REQUIRED + OPTIONAL
DATE_KEYS = ("Raised", "Due", "Closed")
NO_PHONE_CHECK = DATE_KEYS + ("Source", "Tool", "Item")
STATUSES = ("open", "done", "dropped")
CLOSED = ("done", "dropped")
SOON_DAYS = 7
SKILL = "/pm-skills:action-log"


@dataclass(frozen=True)
class Action:
    id: str
    title: str
    line: int
    fields: dict[str, str] = field(default_factory=dict)
    field_lines: dict[str, int] = field(default_factory=dict)

    @property
    def status(self) -> str:
        return self.fields.get("Status", "")

    @property
    def owner(self) -> str:
        return self.fields.get("Owner", "")

    def day(self, key: str) -> Optional[date]:
        value = self.fields.get(key, "")
        if not md.DATE_RE.match(value):
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    @property
    def due(self) -> Optional[date]:
        return self.day("Due")

    @property
    def linked_item(self) -> str:
        """The linked work item as "<tool> <key>", or an empty string."""
        tool, item = self.fields.get("Tool"), self.fields.get("Item")
        return f"{tool} {item}" if tool and item else ""


def parse(text: str) -> tuple[tuple[Action, ...], list[str]]:
    errors: list[str] = []
    actions: list[Action] = []
    title_seen = False
    current: Optional[Action] = None
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if line == TITLE and not title_seen and current is None:
            title_seen = True
        elif line.startswith("## "):
            current = _heading(line, number, errors)
            if current:
                actions.append(current)
        else:
            parsed = md.entry(line) if current else None
            if parsed is None:
                errors.append(f"line {number}: unexpected content: only the title, '## AC-NNN <title>' headings "
                              "and '- Key: value' entries are allowed")
            else:
                _field(current, parsed[0], parsed[1], number, errors)
    if not title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    _order(actions, errors)
    for action in actions:
        _checks(action, errors)
    return tuple(actions), md.sort_errors(errors)


def _heading(line: str, number: int, errors: list[str]) -> Optional[Action]:
    match = HEADING_RE.match(line)
    if not match:
        errors.append(f"line {number}: an action heading is '## AC-NNN <title>' (at least three digits)")
        return None
    return Action(match.group(1), match.group(2).strip(), number)


def _field(action: Action, key: str, value: str, number: int, errors: list[str]) -> None:
    if key not in KEYS:
        errors.append(f"line {number}: unknown key '{key}'; the keys are: {', '.join(KEYS)}")
    elif key in action.fields:
        errors.append(f"line {number}: '{key}' is already on line {action.field_lines[key]}")
    elif not value:
        errors.append(f"line {number}: '{key}' is empty")
    else:
        action.fields[key] = value
        action.field_lines[key] = number
        md.check_contacts(number, key, value, errors, phone=key not in NO_PHONE_CHECK)


def _order(actions: list[Action], errors: list[str]) -> None:
    first: dict[int, int] = {}
    previous: Optional[Action] = None
    for a in actions:
        number = int(a.id[3:])
        if number in first:
            errors.append(f"line {a.line}: duplicate ID '{a.id}' (first on line {first[number]})")
        elif previous and number < int(previous.id[3:]):
            errors.append(f"line {a.line}: {a.id} comes after {previous.id}: keep actions in ID order")
        first.setdefault(number, a.line)
        previous = a


def _checks(action: Action, errors: list[str]) -> None:
    for key in REQUIRED:
        if key not in action.fields:
            errors.append(f"line {action.line}: {action.id} needs '{key}'")
    status = action.status
    if status and status not in STATUSES:
        errors.append(f"line {action.field_lines['Status']}: Status '{status}' must be one of: "
                      f"{', '.join(STATUSES)}")
    if status == "open" and "Due" not in action.fields:
        errors.append(f"line {action.line}: open {action.id} needs 'Due'")
    if status in CLOSED and "Closed" not in action.fields:
        errors.append(f"line {action.line}: {status} {action.id} needs 'Closed'")
    if status in STATUSES and status not in CLOSED:
        for key in ("Closed", "Outcome"):
            if key in action.fields:
                errors.append(f"line {action.field_lines[key]}: only a done or dropped action has '{key}'")
    if ("Tool" in action.fields) != ("Item" in action.fields):
        errors.append(f"line {action.line}: {action.id} has Tool and Item only together: "
                      "the tool as named in the tools register and the item key")
    days = {key: md.parse_date(action.fields[key], action.field_lines[key], key, errors)
            for key in DATE_KEYS if key in action.fields}
    for later in ("Due", "Closed"):
        if days.get(later) and days.get("Raised") and days[later] < days["Raised"]:
            errors.append(f"line {action.field_lines[later]}: {later} {days[later]} is before "
                          f"Raised {days['Raised']}")


def validate(text: str) -> list[str]:
    return parse(text)[1]


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Action log {name} is declared but missing: run {SKILL} to create it."
    actions, errors = parse(text)
    if errors:
        return f"Action log {name} has {md.count_of(len(errors), 'validation error')}: run {SKILL} to fix them."
    live = [a for a in actions if a.status == "open"]
    if not live:
        return f"Action log {name}: no open actions."
    overdue = sum(1 for a in live if a.due and a.due < today)
    soon = sum(1 for a in live if a.due and today <= a.due <= today + timedelta(days=SOON_DAYS))
    parts = [f"{len(live)} open"]
    if overdue:
        parts.append(f"{overdue} overdue")
    if soon:
        parts.append(f"{soon} due in the next {SOON_DAYS} days")
    head = f"Action log {name}: " + ", ".join(parts)
    return f"{head}: run {SKILL} to review them." if overdue else f"{head}."


if __name__ == "__main__":
    sys.exit(md.validate_cli(sys.argv[1:], "actions_register.py", validate))
