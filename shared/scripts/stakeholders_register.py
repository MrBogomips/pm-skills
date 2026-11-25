#!/usr/bin/env python3
"""Parse and validate a stakeholder register (STAKEHOLDERS.md).

The format is specified in shared/registers/stakeholders.md. Python 3 standard library only.

Usage:
    stakeholders_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# Stakeholders"
COLUMNS = ("ID", "Stakeholder", "Organization", "Name", "Interest", "Influence", "Current", "Desired", "Approach",
           "Owner", "Status", "Review")
LAST_REVIEWED = "Last reviewed:"
ID_RE = re.compile(r"^S-[0-9]{3,}$")
LEVELS = ("low", "medium", "high")
ENGAGEMENT = ("unaware", "resistant", "neutral", "supportive", "leading")
STATUSES = ("active", "inactive")
FREE_TEXT = ("Stakeholder", "Organization", "Name", "Approach", "Owner")
SKILL = "/pm-skills:stakeholder-register"


@dataclass(frozen=True)
class Stakeholder:
    id: str
    stakeholder: str
    interest: str
    influence: str
    current: str
    desired: str
    owner: str
    status: str
    review: Optional[date]
    line: int

    @property
    def below_desired(self) -> bool:
        if self.current not in ENGAGEMENT or self.desired not in ENGAGEMENT:
            return False
        return ENGAGEMENT.index(self.current) < ENGAGEMENT.index(self.desired)


@dataclass(frozen=True)
class Register:
    last_reviewed: Optional[date]
    stakeholders: tuple[Stakeholder, ...]


def _one_of(c: dict[str, str], column: str, options: tuple[str, ...], n: int, errors: list[str]) -> None:
    if c[column] not in options:
        errors.append(f"line {n}: {column} '{c[column]}' must be one of: {', '.join(options)}")


def _stakeholder(row: md.Row, errors: list[str]) -> Stakeholder:
    c, n = row.cells, row.line
    if not ID_RE.match(c["ID"]):
        errors.append(f"line {n}: ID '{c['ID']}' must be S- followed by at least three digits (S-001)")
    if not c["Stakeholder"]:
        errors.append(f"line {n}: Stakeholder is empty: name the role or the group")
    for column in ("Interest", "Influence"):
        _one_of(c, column, LEVELS, n, errors)
    for column in ("Current", "Desired"):
        _one_of(c, column, ENGAGEMENT, n, errors)
    _one_of(c, "Status", STATUSES, n, errors)
    review = md.parse_date(c["Review"], n, "Review", errors) if c["Review"] else None
    if c["Current"] != c["Desired"] and not c["Approach"]:
        errors.append(f"line {n}: Current differs from Desired: the row needs Approach")
    if c["Status"] == "active":
        for column in ("Owner", "Review"):
            if not c[column]:
                errors.append(f"line {n}: an active stakeholder needs {column}")
    for column in FREE_TEXT:
        md.check_contacts(n, column, c[column], errors)
    return Stakeholder(c["ID"], c["Stakeholder"], c["Interest"], c["Influence"], c["Current"], c["Desired"],
                       c["Owner"], c["Status"], review, n)


def parse(text: str) -> tuple[Register, list[str]]:
    errors: list[str] = []
    table = md.Table(COLUMNS)
    title_seen, table_seen, last_reviewed = False, False, None
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            if table_seen:
                table.close()
        elif line == TITLE and not title_seen and not table_seen:
            title_seen = True
        elif line.startswith(LAST_REVIEWED) and not table_seen:
            last_reviewed = md.parse_date(line[len(LAST_REVIEWED):].strip(), number, "Last reviewed", errors)
        elif line.startswith("|") and title_seen and table.open:
            table_seen = True
            table.feed(number, line, errors)
        else:
            errors.append(f"line {number}: unexpected content: only the title, '{LAST_REVIEWED}' and the "
                          "stakeholders table are allowed")
    if not title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    if not table_seen:
        errors.append(f"line 1: missing the stakeholders table ({' | '.join(COLUMNS)})")
    stakeholders = tuple(_stakeholder(row, errors) for row in table.rows)
    first: dict[str, int] = {}
    for s in stakeholders:
        if s.id in first:
            errors.append(f"line {s.line}: duplicate ID '{s.id}' (first on line {first[s.id]})")
        first.setdefault(s.id, s.line)
    return Register(last_reviewed, stakeholders), md.sort_errors(errors)


def validate(text: str) -> list[str]:
    return parse(text)[1]


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Stakeholder register {name} is declared but missing: run {SKILL} to create it."
    register, errors = parse(text)
    if errors:
        return f"Stakeholder register {name} has {md.count_of(len(errors), 'validation error')}: run {SKILL} to fix them."
    active = [s for s in register.stakeholders if s.status == "active"]
    below = sum(1 for s in active if s.below_desired)
    overdue = sum(1 for s in active if s.review and s.review < today)
    head = f"Stakeholder register {name}: {len(active)} active, {below} below their desired engagement"
    if overdue:
        return f"{head}, {overdue} past their review date: run {SKILL} to review them."
    return f"{head}."


if __name__ == "__main__":
    sys.exit(md.validate_cli(sys.argv[1:], "stakeholders_register.py", validate))
