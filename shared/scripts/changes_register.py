#!/usr/bin/env python3
"""Parse and validate a change log (CHANGES.md).

The format is specified in shared/registers/changes.md. Python 3 standard library only.

Usage:
    changes_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# Changes"
HEADING_RE = re.compile(r"^## (CR-[0-9]{3,})\s+(\S.*)$")
REQUIRED = ("Raised", "Requested by", "Status", "Description", "Reason")
IMPACTS = ("Scope impact", "Schedule impact", "Cost impact", "Risk impact")
DECISION_KEYS = ("Decided by", "Decided on")
KEYS = REQUIRED + IMPACTS + ("Recommendation",) + DECISION_KEYS + ("Decision", "Implemented on", "Source")
DATE_KEYS = ("Raised", "Decided on", "Implemented on")
NO_PHONE_CHECK = DATE_KEYS + ("Decision",)
STATUSES = ("proposed", "assessed", "approved", "rejected", "withdrawn", "implemented")
OPEN = ("proposed", "assessed")
DECIDED = ("approved", "rejected", "implemented")
ASSESSED = ("assessed",) + DECIDED
DECISION_REF_RE = re.compile(r"^D-[0-9]{3,}$")
SKILL = "/pm-skills:change-request"


@dataclass(frozen=True)
class ChangeRequest:
    id: str
    title: str
    line: int
    fields: dict[str, str] = field(default_factory=dict)
    field_lines: dict[str, int] = field(default_factory=dict)

    @property
    def status(self) -> str:
        return self.fields.get("Status", "")

    def day(self, key: str) -> Optional[date]:
        value = self.fields.get(key, "")
        if not md.DATE_RE.match(value):
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    @property
    def decided_on(self) -> Optional[date]:
        return self.day("Decided on")


def parse(text: str) -> tuple[tuple[ChangeRequest, ...], list[str]]:
    errors: list[str] = []
    changes: list[ChangeRequest] = []
    title_seen = False
    current: Optional[ChangeRequest] = None
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if line == TITLE and not title_seen and current is None:
            title_seen = True
        elif line.startswith("## "):
            current = _heading(line, number, errors)
            if current:
                changes.append(current)
        else:
            parsed = md.entry(line) if current else None
            if parsed is None:
                errors.append(f"line {number}: unexpected content: only the title, '## CR-NNN <title>' headings "
                              "and '- Key: value' entries are allowed")
            else:
                _field(current, parsed[0], parsed[1], number, errors)
    if not title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    _order(changes, errors)
    for change in changes:
        _checks(change, errors)
    return tuple(changes), md.sort_errors(errors)


def _heading(line: str, number: int, errors: list[str]) -> Optional[ChangeRequest]:
    match = HEADING_RE.match(line)
    if not match:
        errors.append(f"line {number}: a change request heading is '## CR-NNN <title>'")
        return None
    return ChangeRequest(match.group(1), match.group(2).strip(), number)


def _field(change: ChangeRequest, key: str, value: str, number: int, errors: list[str]) -> None:
    if key not in KEYS:
        errors.append(f"line {number}: unknown key '{key}'; the keys are: {', '.join(KEYS)}")
    elif key in change.fields:
        errors.append(f"line {number}: '{key}' is already on line {change.field_lines[key]}")
    elif not value:
        errors.append(f"line {number}: '{key}' is empty")
    else:
        change.fields[key] = value
        change.field_lines[key] = number
        md.check_contacts(number, key, value, errors, phone=key not in NO_PHONE_CHECK)


def _order(changes: list[ChangeRequest], errors: list[str]) -> None:
    first: dict[int, int] = {}
    previous: Optional[ChangeRequest] = None
    for c in changes:
        number = int(c.id[3:])
        if number in first:
            errors.append(f"line {c.line}: duplicate ID '{c.id}' (first on line {first[number]})")
        elif previous and number < int(previous.id[3:]):
            errors.append(f"line {c.line}: {c.id} comes after {previous.id}: keep change requests in ID order")
        first.setdefault(number, c.line)
        previous = c


def _require(change: ChangeRequest, keys: tuple[str, ...], errors: list[str]) -> None:
    for key in keys:
        if key not in change.fields:
            errors.append(f"line {change.line}: {change.id} needs '{key}'")


def _forbid(change: ChangeRequest, keys: tuple[str, ...], who: str, errors: list[str]) -> None:
    for key in keys:
        if key in change.fields:
            errors.append(f"line {change.field_lines[key]}: only {who} has '{key}'")


def _checks(change: ChangeRequest, errors: list[str]) -> None:
    _require(change, REQUIRED, errors)
    status = change.status
    if status and status not in STATUSES:
        errors.append(f"line {change.field_lines['Status']}: Status '{status}' must be one of: {', '.join(STATUSES)}")
        return
    if status in ASSESSED:
        _require(change, IMPACTS, errors)
    if status in DECIDED:
        _require(change, DECISION_KEYS, errors)
    elif status:
        _forbid(change, DECISION_KEYS, "an approved, rejected or implemented request", errors)
    if status == "implemented":
        _require(change, ("Implemented on",), errors)
    elif status:
        _forbid(change, ("Implemented on",), "an implemented request", errors)
    decision = change.fields.get("Decision")
    if decision and not DECISION_REF_RE.match(decision):
        errors.append(f"line {change.field_lines['Decision']}: Decision '{decision}' must be one decision log "
                      "ID (D-NNN)")
    _dates(change, errors)


def _dates(change: ChangeRequest, errors: list[str]) -> None:
    days: dict[str, Optional[date]] = {}
    for key in DATE_KEYS:
        if key in change.fields:
            days[key] = md.parse_date(change.fields[key], change.field_lines[key], key, errors)
    for later, earlier in (("Decided on", "Raised"), ("Implemented on", "Decided on")):
        if days.get(later) and days.get(earlier) and days[later] < days[earlier]:
            errors.append(f"line {change.field_lines[later]}: {later} {days[later]} is before "
                          f"{earlier} {days[earlier]}")


def validate(text: str) -> list[str]:
    return parse(text)[1]


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Change log {name} is declared but missing: run {SKILL} to create it."
    changes, errors = parse(text)
    if errors:
        return f"Change log {name} has {len(errors)} validation errors: run {SKILL} to fix them."
    if not changes:
        return f"Change log {name}: no change requests yet."
    counts = {s: sum(1 for c in changes if c.status == s) for s in OPEN}
    decided = [c for c in changes if c.status in DECIDED and c.decided_on]
    head = (f"Change log {name}: {sum(counts.values())} open "
            f"({counts['proposed']} proposed, {counts['assessed']} assessed), {len(decided)} decided")
    if not decided:
        return f"{head}."
    latest = max(decided, key=lambda c: (c.decided_on, int(c.id[3:])))
    return f"{head}, latest decision {latest.id} on {latest.decided_on}."


if __name__ == "__main__":
    sys.exit(md.validate_cli(sys.argv[1:], "changes_register.py", validate))
