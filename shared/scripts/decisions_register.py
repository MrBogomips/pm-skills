#!/usr/bin/env python3
"""Parse and validate a decision log (DECISIONS.md).

The format is specified in shared/registers/decisions.md. Python 3 standard library only.

Usage:
    decisions_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# Decisions"
HEADING_RE = re.compile(r"^## (D-[0-9]{3,})\s+(\S.*)$")
REQUIRED = ("Date", "Status", "Decided by", "Context", "Decision")
OPTIONAL = ("Options", "Consequences", "Supersedes", "Superseded by", "Source")
KEYS = REQUIRED + OPTIONAL
STATUSES = ("accepted", "superseded", "revoked")
REF_RE = re.compile(r"^D-[0-9]{3,}$")
SKILL = "/pm-skills:decision-log"


@dataclass
class Decision:
    id: str
    title: str
    line: int
    fields: dict[str, str] = field(default_factory=dict)
    field_lines: dict[str, int] = field(default_factory=dict)

    @property
    def date(self) -> Optional[date]:
        try:
            return date.fromisoformat(self.fields.get("Date", ""))
        except ValueError:
            return None


def parse(text: str) -> tuple[tuple[Decision, ...], list[str]]:
    errors: list[str] = []
    decisions: list[Decision] = []
    title_seen = False
    current: Optional[Decision] = None
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if line == TITLE and not title_seen and current is None:
            title_seen = True
            continue
        if line.startswith("## "):
            match = HEADING_RE.match(line)
            if not match:
                errors.append(f"line {number}: a decision heading is '## D-NNN <title>'")
                current = None
                continue
            current = Decision(match.group(1), match.group(2).strip(), number)
            decisions.append(current)
            continue
        parsed = md.entry(line) if current else None
        if parsed is None:
            errors.append(f"line {number}: unexpected content: only the title, '## D-NNN <title>' headings and "
                          "'- Key: value' entries are allowed")
            continue
        _field(current, parsed[0], parsed[1], number, errors)
    if not title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    _checks(decisions, errors)
    return tuple(decisions), md.sort_errors(errors)


def _field(decision: Decision, key: str, value: str, number: int, errors: list[str]) -> None:
    if key not in KEYS:
        errors.append(f"line {number}: unknown key '{key}'; the keys are: {', '.join(KEYS)}")
    elif key in decision.fields:
        errors.append(f"line {number}: '{key}' is already on line {decision.field_lines[key]}")
    elif not value:
        errors.append(f"line {number}: '{key}' is empty")
    else:
        decision.fields[key] = value
        decision.field_lines[key] = number
        md.check_contacts(number, key, value, errors, phone=key not in ("Date", "Supersedes", "Superseded by"))


def _checks(decisions: list[Decision], errors: list[str]) -> None:
    by_id: dict[str, Decision] = {}
    previous: Optional[Decision] = None
    for d in decisions:
        if d.id in by_id:
            errors.append(f"line {d.line}: duplicate ID '{d.id}' (first on line {by_id[d.id].line})")
        elif previous and int(d.id[2:]) < int(previous.id[2:]):
            errors.append(f"line {d.line}: {d.id} comes after {previous.id}: keep decisions in ID order")
        by_id.setdefault(d.id, d)
        previous = d
        for key in REQUIRED:
            if key not in d.fields:
                errors.append(f"line {d.line}: {d.id} needs '{key}'")
        if "Date" in d.fields:
            md.parse_date(d.fields["Date"], d.field_lines["Date"], "Date", errors)
        status = d.fields.get("Status")
        if status and status not in STATUSES:
            errors.append(f"line {d.field_lines['Status']}: Status '{status}' must be one of: {', '.join(STATUSES)}")
        if status == "superseded" and "Superseded by" not in d.fields:
            errors.append(f"line {d.line}: superseded {d.id} needs 'Superseded by'")
        if "Superseded by" in d.fields and status != "superseded":
            errors.append(f"line {d.field_lines['Superseded by']}: only a superseded decision has 'Superseded by'")
    for d in decisions:
        for key, back in (("Supersedes", "Superseded by"), ("Superseded by", "Supersedes")):
            ref = d.fields.get(key)
            if ref is None:
                continue
            line = d.field_lines[key]
            if not REF_RE.match(ref):
                errors.append(f"line {line}: {key} '{ref}' must be one decision ID (D-NNN)")
            elif ref not in by_id or ref == d.id:
                errors.append(f"line {line}: {key} '{ref}' is not another decision of this log")
            elif by_id[ref].fields.get(back) != d.id:
                errors.append(f"line {line}: {ref} must have '{back}: {d.id}'")


def validate(text: str) -> list[str]:
    return parse(text)[1]


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Decision log {name} is declared but missing: run {SKILL} to create it."
    decisions, errors = parse(text)
    if errors:
        return f"Decision log {name} has {len(errors)} validation errors: run {SKILL} to fix them."
    if not decisions:
        return f"Decision log {name}: no decisions yet."
    accepted = sum(1 for d in decisions if d.fields.get("Status") == "accepted")
    latest = decisions[-1]
    return (f"Decision log {name}: {len(decisions)} decisions, {accepted} in force, "
            f"latest {latest.id} on {latest.fields.get('Date', '?')}.")


if __name__ == "__main__":
    sys.exit(md.validate_cli(sys.argv[1:], "decisions_register.py", validate))
