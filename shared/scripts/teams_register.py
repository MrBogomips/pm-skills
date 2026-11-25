#!/usr/bin/env python3
"""Parse and validate a team register (TEAMS.md).

The format is specified in shared/registers/teams.md. Errors are strings of the form
"line N: <message>". Python 3 standard library only.

Usage:
    teams_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# Team"
ACTIVE_HEADING = "## Active team"
HISTORY_HEADING = "## History"
ACTIVE_COLUMNS = ("Slug", "Name", "Organization", "GitHub", "Jira", "Roles", "Areas")
ACTIVE_COLUMNS_WITH_GIT = ("Slug", "Name", "Organization", "GitHub", "Jira", "Git", "Roles", "Areas")
HISTORY_COLUMNS = ("Slug", "From", "To", "Role")
LAST_RECONCILED = "Last reconciled:"
SOURCES = "Sources:"  # removed in 1.0: the tools live in TOOLS.md

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
GITHUB_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
GIT_IDENTITY_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
STALE_AFTER_DAYS = 42
SKILL = "/pm-skills:team-register"
SEPARATOR_CELL_RE = re.compile(r"^:?-+:?$")
NO_PHONE_CHECK = {"Slug", "GitHub", "Jira", "Git", "From", "To"}
DATES_AND_RANGES_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{4}\s*[-–]\s*\d{4}\b")


@dataclass(frozen=True)
class Member:
    slug: str
    name: str
    organization: str
    github: str
    jira: str
    roles: tuple[str, ...]
    areas: tuple[str, ...]
    line: int
    git: tuple[str, ...] = ()


@dataclass(frozen=True)
class Period:
    slug: str
    start: date
    end: Optional[date]
    role: str
    line: int


@dataclass(frozen=True)
class Register:
    last_reconciled: Optional[date]
    active: tuple[Member, ...]
    history: tuple[Period, ...]


@dataclass(frozen=True)
class _Row:
    line: int
    cells: dict[str, str]


def _cells(line: str) -> list[str]:
    parts = line.strip().split("|")
    return [p.strip() for p in parts[1:-1]] if line.strip().endswith("|") else [p.strip() for p in parts[1:]]


def _parse_date(value: str, line: int, what: str, errors: list[str]) -> Optional[date]:
    if not DATE_RE.match(value):
        errors.append(f"line {line}: {what} '{value}' is not a date (YYYY-MM-DD)")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"line {line}: {what} '{value}' is not a valid date")
        return None


def _split_list(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(","))


class _Scanner:
    """Line-by-line state machine: preamble -> Active team -> History."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.title_seen = False
        self.last_reconciled: Optional[date] = None
        self.section: Optional[str] = None  # None, "active", "history"
        self.table_state = "none"  # none, header, separator, rows, closed
        self.rows: dict[str, list[_Row]] = {"active": [], "history": []}
        self.active_columns = ACTIVE_COLUMNS
        self.last_line = 0

    def scan(self, text: str) -> None:
        for number, raw in enumerate(text.splitlines(), start=1):
            self.last_line = number
            self._line(number, raw.strip())
        for heading, key in ((ACTIVE_HEADING, "active"), (HISTORY_HEADING, "history")):
            if self.section is None or (key == "history" and self.section != "history"):
                self.errors.append(f"line {self.last_line}: missing section '{heading}'")
        if not self.title_seen:
            self.errors.append(f"line 1: missing title '{TITLE}'")

    def _line(self, number: int, line: str) -> None:
        if not line:
            if self.table_state == "rows":
                self.table_state = "closed"
            return
        if line == TITLE and not self.title_seen and self.section is None:
            self.title_seen = True
        elif line == ACTIVE_HEADING and self.section is None:
            self.section, self.table_state = "active", "header"
        elif line == HISTORY_HEADING and self.section == "active":
            self.section, self.table_state = "history", "header"
        elif line.startswith(LAST_RECONCILED) and self.section is None:
            value = line[len(LAST_RECONCILED):].strip()
            self.last_reconciled = _parse_date(value, number, "Last reconciled", self.errors)
        elif line.startswith(SOURCES) and self.section is None:
            self.errors.append(f"line {number}: the '{SOURCES}' line is no longer used: the project's tools are "
                               "declared in its tools register (TOOLS.md); remove the line")
        elif line.startswith("|") and self.section and self.table_state != "closed":
            self._table_line(number, line)
        else:
            self.errors.append(f"line {number}: unexpected content: only the title, '{LAST_RECONCILED}', "
                               "the two sections and their tables are allowed")

    def _table_line(self, number: int, line: str) -> None:
        columns = self.active_columns if self.section == "active" else HISTORY_COLUMNS
        cells = _cells(line)
        if self.table_state == "header":
            if self.section == "active" and tuple(cells) == ACTIVE_COLUMNS_WITH_GIT:
                self.active_columns = ACTIVE_COLUMNS_WITH_GIT
            elif tuple(cells) != columns:
                optional = " (optionally with Git after Jira)" if self.section == "active" else ""
                self.errors.append(f"line {number}: columns must be exactly: {' | '.join(columns)}{optional}")
            self.table_state = "separator"
        elif self.table_state == "separator":
            if len(cells) != len(columns) or not all(SEPARATOR_CELL_RE.match(c) for c in cells):
                self.errors.append(f"line {number}: expected the table separator row")
            self.table_state = "rows"
        elif len(cells) != len(columns):
            self.errors.append(f"line {number}: expected {len(columns)} cells, found {len(cells)}")
        else:
            self.rows[self.section].append(_Row(number, dict(zip(columns, cells))))


def _check_personal_data(row: _Row, errors: list[str]) -> None:
    for column, value in row.cells.items():
        if column == "Git":
            continue
        if EMAIL_RE.search(value):
            errors.append(f"line {row.line}: {column} contains an email address: contacts do not belong here")
        elif column not in NO_PHONE_CHECK and PHONE_RE.search(DATES_AND_RANGES_RE.sub(" ", value)):
            errors.append(f"line {row.line}: {column} contains a phone number: contacts do not belong here")


def _member(row: _Row, errors: list[str]) -> Member:
    c = row.cells
    if not SLUG_RE.match(c["Slug"]):
        errors.append(f"line {row.line}: slug '{c['Slug']}' must be lowercase letters, digits and single hyphens")
    if not c["Name"]:
        errors.append(f"line {row.line}: name is empty")
    if c["GitHub"] and not GITHUB_RE.match(c["GitHub"]):
        errors.append(f"line {row.line}: GitHub '{c['GitHub']}' must be a login without '@'")
    if c["Jira"] and (re.search(r"\s", c["Jira"]) or "@" in c["Jira"]):
        errors.append(f"line {row.line}: Jira '{c['Jira']}' must be an account ID, without spaces or '@'")
    roles, areas = _split_list(c["Roles"]), _split_list(c["Areas"]) if c["Areas"] else ()
    if not c["Roles"] or any(not r for r in roles):
        errors.append(f"line {row.line}: Roles must be a non-empty comma-separated list")
    if any(not a for a in areas):
        errors.append(f"line {row.line}: Areas has an empty item")
    git = _split_list(c["Git"]) if c.get("Git") else ()
    for identity in git:
        if not GIT_IDENTITY_RE.match(identity):
            errors.append(f"line {row.line}: Git '{identity}' must be a commit email (name@domain)")
    _check_personal_data(row, errors)
    return Member(c["Slug"], c["Name"], c["Organization"], c["GitHub"], c["Jira"],
                  roles if c["Roles"] else (), areas, row.line, git)


def _period(row: _Row, errors: list[str]) -> Optional[Period]:
    c = row.cells
    if not SLUG_RE.match(c["Slug"]):
        errors.append(f"line {row.line}: slug '{c['Slug']}' must be lowercase letters, digits and single hyphens")
    start = _parse_date(c["From"], row.line, "From", errors)
    end = _parse_date(c["To"], row.line, "To", errors) if c["To"] else None
    _check_personal_data(row, errors)
    if start is None or (c["To"] and end is None):
        return None
    if end is not None and start > end:
        errors.append(f"line {row.line}: From {start} is after To {end}")
    return Period(c["Slug"], start, end, c["Role"], row.line)


def _cross_checks(active: tuple[Member, ...], history: tuple[Period, ...], errors: list[str]) -> None:
    seen: dict[str, int] = {}
    for member in active:
        if member.slug in seen:
            errors.append(f"line {member.line}: duplicate slug '{member.slug}' (first on line {seen[member.slug]})")
        seen.setdefault(member.slug, member.line)
    accounts = (("GitHub", lambda m: (m.github,)), ("Jira", lambda m: (m.jira,)), ("Git", lambda m: m.git))
    for column, values in accounts:
        first: dict[str, Member] = {}
        for member in active:
            for value in values(member):
                key = value.lower() if column != "Jira" else value
                if not key:
                    continue
                if key in first and first[key] is not member:
                    errors.append(f"line {member.line}: {column} '{value}' is also on line {first[key].line}: "
                                  "one account belongs to one person")
                first.setdefault(key, member)
    for member in active:
        open_periods = [p for p in history if p.slug == member.slug and p.end is None]
        if len(open_periods) != 1:
            errors.append(f"line {member.line}: '{member.slug}' needs exactly one open period in History "
                          f"(found {len(open_periods)})")
    for period in history:
        if period.end is None and period.slug not in seen:
            errors.append(f"line {period.line}: open period for '{period.slug}', who is not in Active team")
    by_slug: dict[str, list[Period]] = {}
    for period in history:
        by_slug.setdefault(period.slug, []).append(period)
    for periods in by_slug.values():
        ordered = sorted(periods, key=lambda p: (p.start, p.line))
        for previous, current in zip(ordered, ordered[1:]):
            if previous.end is None or current.start <= previous.end:
                later = max(previous, current, key=lambda p: p.line)
                other = previous if later is current else current
                errors.append(f"line {later.line}: period overlaps the one on line {other.line}")


def parse(text: str) -> tuple[Optional[Register], list[str]]:
    """Parse a register; the Register is None only when a section is missing."""
    scanner = _Scanner()
    scanner.scan(text)
    errors = scanner.errors
    if scanner.section != "history":
        return None, errors
    active = tuple(_member(row, errors) for row in scanner.rows["active"])
    history = tuple(p for p in (_period(row, errors) for row in scanner.rows["history"]) if p is not None)
    _cross_checks(active, history, errors)
    errors.sort(key=lambda e: int(e.split(":", 1)[0].split()[1]))
    return Register(scanner.last_reconciled, active, history), errors


def validate(text: str) -> list[str]:
    return parse(text)[1]


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    """One line of session context about the register at path."""
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Team register {name} is declared but missing: run {SKILL} to create it."
    register, errors = parse(text)
    if errors or register is None:
        return f"Team register {name} has {md.count_of(len(errors), 'validation error')}: run {SKILL} to fix them."
    head = f"Team register {name}: {len(register.active)} active"
    if register.last_reconciled is None:
        return f"{head}, never reconciled."
    days = (today - register.last_reconciled).days
    if days > STALE_AFTER_DAYS:
        return f"{head}, last reconciled {register.last_reconciled} ({days} days ago: run {SKILL} to reconcile)."
    return f"{head}, last reconciled {register.last_reconciled}."


def _cli(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] != "validate":
        print("usage: teams_register.py validate FILE", file=sys.stderr)
        return 2
    try:
        text = Path(argv[1]).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"cannot read {argv[1]}: {exc}", file=sys.stderr)
        return 2
    errors = validate(text)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
