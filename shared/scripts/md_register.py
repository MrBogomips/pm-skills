"""Helpers shared by the register validators: Markdown tables, `- Key: value` entries, dates and personal data.

Errors are strings of the form "line N: <message>". Python 3 standard library only.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Optional

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEPARATOR_CELL_RE = re.compile(r"^:?-+:?$")
EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
DATES_AND_RANGES_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{4}\s*[-–]\s*\d{4}\b")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
ENTRY_RE = re.compile(r"^-\s+([A-Za-z][A-Za-z ]*?):\s*(.*)$")
PATH_RE = re.compile(r"^`([^`]+)`")


@dataclass(frozen=True)
class Row:
    line: int
    cells: dict[str, str]


@dataclass(frozen=True)
class Entry:
    line: int
    key: str
    value: str


def cells(line: str) -> list[str]:
    """The cells of a Markdown table row, stripped."""
    parts = line.strip().split("|")
    return [p.strip() for p in parts[1:-1]] if line.strip().endswith("|") else [p.strip() for p in parts[1:]]


def is_separator(values: list[str], width: int) -> bool:
    return len(values) == width and all(SEPARATOR_CELL_RE.match(c) for c in values)


def parse_date(value: str, line: int, what: str, errors: list[str]) -> Optional[date]:
    if not DATE_RE.match(value):
        errors.append(f"line {line}: {what} '{value}' is not a date (YYYY-MM-DD)")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"line {line}: {what} '{value}' is not a valid date")
        return None


def split_list(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(","))


def entry(line: str) -> Optional[tuple[str, str]]:
    """A `- Key: value` line as (key, value), or None."""
    match = ENTRY_RE.match(line.strip())
    return (match.group(1).strip(), match.group(2).strip()) if match else None


def backtick_path(value: str) -> Optional[str]:
    """The path in a value that starts with a backtick-quoted path; text after it is ignored."""
    match = PATH_RE.match(value.strip())
    return match.group(1) if match else None


def check_contacts(line: int, column: str, value: str, errors: list[str], phone: bool = True) -> None:
    """Reject email addresses and phone numbers: contacts do not belong in project registers."""
    if EMAIL_RE.search(value):
        errors.append(f"line {line}: {column} contains an email address: contacts do not belong here")
    elif phone and PHONE_RE.search(DATES_AND_RANGES_RE.sub(" ", value)):
        errors.append(f"line {line}: {column} contains a phone number: contacts do not belong here")


class Table:
    """Collects the rows of one Markdown table with fixed columns, header and separator first."""

    def __init__(self, columns: tuple[str, ...]) -> None:
        self.columns = columns
        self.state = "header"  # header, separator, rows, closed
        self.rows: list[Row] = []

    def feed(self, number: int, line: str, errors: list[str]) -> None:
        values = cells(line)
        if self.state == "header":
            if tuple(values) != self.columns:
                errors.append(f"line {number}: columns must be exactly: {' | '.join(self.columns)}")
            self.state = "separator"
        elif self.state == "separator":
            if not is_separator(values, len(self.columns)):
                errors.append(f"line {number}: expected the table separator row")
            self.state = "rows"
        elif len(values) != len(self.columns):
            errors.append(f"line {number}: expected {len(self.columns)} cells, found {len(values)}")
        else:
            self.rows.append(Row(number, dict(zip(self.columns, values))))

    def close(self) -> None:
        if self.state == "rows":
            self.state = "closed"

    @property
    def open(self) -> bool:
        return self.state != "closed"


def sort_errors(errors: list[str]) -> list[str]:
    def key(error: str) -> int:
        try:
            return int(error.split(":", 1)[0].split()[1])
        except (IndexError, ValueError):
            return 0
    return sorted(errors, key=key)


def validate_cli(argv: list[str], name: str, validate: Callable[[str], list[str]]) -> int:
    """The `validate FILE` command line shared by the register scripts: exit 0 valid, 1 invalid, 2 usage or I/O."""
    import sys

    if len(argv) != 2 or argv[0] != "validate":
        print(f"usage: {name} validate FILE", file=sys.stderr)
        return 2
    try:
        text = Path(argv[1]).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read {argv[1]}: {exc}", file=sys.stderr)
        return 2
    errors = validate(text)
    for error in errors:
        print(error)
    return 1 if errors else 0
