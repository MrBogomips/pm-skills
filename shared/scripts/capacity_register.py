#!/usr/bin/env python3
"""Parse and validate a capacity register (CAPACITY.md).

The format is specified in shared/registers/capacity.md. Python 3 standard library only.

Usage:
    capacity_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
    capacity_register.py available FILE --from YYYY-MM-DD --to YYYY-MM-DD [--member SLUG]
        print the available person-days in the period, with the working; exit 2 on usage, I/O or an invalid file
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# Capacity"
WORKING_DAYS = "Working days:"
WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
DEFAULT_WORKING_DAYS = ("mon", "tue", "wed", "thu", "fri")
SECTIONS = ("## Calendar", "## Allocation")
CALENDAR_COLUMNS = ("From", "To", "Kind", "Description")
ALLOCATION_COLUMNS = ("Member", "From", "To", "Allocation")
KINDS = ("holiday", "closure", "event")
DAYS_OFF = ("holiday", "closure")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LOOKAHEAD_DAYS = 14
SKILL = "/pm-skills:capacity-register"


@dataclass(frozen=True)
class CalendarDay:
    start: Optional[date]
    end: Optional[date]
    kind: str
    description: str
    line: int


@dataclass(frozen=True)
class Allocation:
    member: str
    start: Optional[date]
    end: Optional[date]
    percent: Optional[int]
    base: bool
    line: int


@dataclass(frozen=True)
class Register:
    working_days: tuple[str, ...]
    calendar: tuple[CalendarDay, ...]
    allocations: tuple[Allocation, ...]


def _working_days(value: str, number: int, errors: list[str]) -> tuple[str, ...]:
    days = md.split_list(value)
    bad = [d for d in days if d not in WEEKDAYS]
    if bad:
        errors.append(f"line {number}: Working days: '{', '.join(bad)}' not among {', '.join(WEEKDAYS)}")
        return DEFAULT_WORKING_DAYS
    if len(set(days)) != len(days):
        errors.append(f"line {number}: Working days: a day appears twice")
        return DEFAULT_WORKING_DAYS
    return days


def _range(c: dict[str, str], n: int, errors: list[str]) -> tuple[Optional[date], Optional[date]]:
    start = md.parse_date(c["From"], n, "From", errors)
    end = md.parse_date(c["To"], n, "To", errors) if c["To"] else None
    if start and end and end < start:
        errors.append(f"line {n}: To {end} is before From {start}")
    return start, end


def _calendar_day(row: md.Row, errors: list[str]) -> CalendarDay:
    c, n = row.cells, row.line
    start, end = _range(c, n, errors)
    if c["Kind"] not in KINDS:
        errors.append(f"line {n}: Kind '{c['Kind']}' must be one of: {', '.join(KINDS)}")
    if not c["Description"]:
        errors.append(f"line {n}: Description is empty")
    md.check_contacts(n, "Description", c["Description"], errors)
    return CalendarDay(start, end, c["Kind"], c["Description"], n)


def _allocation(row: md.Row, errors: list[str]) -> Allocation:
    c, n = row.cells, row.line
    if not SLUG_RE.match(c["Member"]):
        errors.append(f"line {n}: Member '{c['Member']}' must be a team register slug (lowercase, such as ada-l)")
    start, end = _range(c, n, errors)
    percent = int(c["Allocation"]) if md.is_number(c["Allocation"]) else None
    if percent is None or percent > 100:
        errors.append(f"line {n}: Allocation '{c['Allocation']}' must be a whole number from 0 to 100, without %")
        percent = None
    return Allocation(c["Member"], start, end, percent, not c["To"], n)


def _overlaps(allocations: tuple[Allocation, ...], errors: list[str]) -> None:
    bases: dict[tuple[str, date], int] = {}
    periods: list[Allocation] = []
    for a in allocations:
        if a.start is None:
            continue
        if a.base:
            key = (a.member, a.start)
            if key in bases:
                errors.append(f"line {a.line}: {a.member} has another base allocation with the same From "
                              f"on line {bases[key]}")
            bases.setdefault(key, a.line)
            continue
        if a.end is None or a.end < a.start:
            continue
        for p in periods:
            if p.member == a.member and a.start <= p.end and p.start <= a.end:
                errors.append(f"line {a.line}: this period of {a.member} overlaps the one on line {p.line}")
                break
        periods.append(a)


class _Scanner:
    """Line-by-line state machine: preamble -> Calendar -> Allocation."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.title_seen = False
        self.working_days = DEFAULT_WORKING_DAYS
        self.section = -1
        self.tables = (md.Table(CALENDAR_COLUMNS), md.Table(ALLOCATION_COLUMNS))
        self.seen_tables = [False, False]

    def scan(self, text: str) -> int:
        last = 0
        for number, raw in enumerate(text.splitlines(), start=1):
            last = number
            self._line(number, raw.strip())
        return last

    def _line(self, number: int, line: str) -> None:
        if not line:
            if self.section >= 0 and self.seen_tables[self.section]:
                self.tables[self.section].close()
        elif line == TITLE and not self.title_seen and self.section < 0:
            self.title_seen = True
        elif line.startswith(WORKING_DAYS) and self.section < 0:
            self.working_days = _working_days(line[len(WORKING_DAYS):].strip(), number, self.errors)
        elif line.startswith("## "):
            self._section(number, line)
        elif line.startswith("|") and self.section >= 0 and self.tables[self.section].open:
            self.seen_tables[self.section] = True
            self.tables[self.section].feed(number, line, self.errors)
        else:
            self.errors.append(f"line {number}: unexpected content: only the title, '{WORKING_DAYS}', the two "
                               "sections and their tables are allowed")

    def _section(self, number: int, line: str) -> None:
        if line in SECTIONS and SECTIONS.index(line) == self.section + 1:
            self.section += 1
        else:
            self.errors.append(f"line {number}: unexpected section '{line}': the sections are "
                               f"{', '.join(SECTIONS)}, once each and in this order")


def parse(text: str) -> tuple[Register, list[str]]:
    scanner = _Scanner()
    last = scanner.scan(text)
    errors = scanner.errors
    if not scanner.title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    for index, heading in enumerate(SECTIONS):
        if scanner.section < index:
            errors.append(f"line {last}: missing section '{heading}'")
        elif not scanner.seen_tables[index]:
            errors.append(f"line {last}: section '{heading}' has no table")
    calendar = tuple(_calendar_day(row, errors) for row in scanner.tables[0].rows)
    allocations = tuple(_allocation(row, errors) for row in scanner.tables[1].rows)
    _overlaps(allocations, errors)
    return Register(scanner.working_days, calendar, allocations), md.sort_errors(errors)


def validate(text: str) -> list[str]:
    return parse(text)[1]


def next_day_off(register: Register, today: date) -> Optional[date]:
    """The first holiday or closure day from today on, today included."""
    candidates = []
    for day in register.calendar:
        if day.kind not in DAYS_OFF or day.start is None:
            continue
        end = day.end or day.start
        if end >= today:
            candidates.append(max(day.start, today))
    return min(candidates) if candidates else None


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Capacity register {name} is declared but missing: run {SKILL} to create it."
    register, errors = parse(text)
    if errors:
        return f"Capacity register {name} has {md.count_of(len(errors), 'validation error')}: run {SKILL} to fix them."
    members = len({a.member for a in register.allocations if a.base})
    horizon = today + timedelta(days=LOOKAHEAD_DAYS)
    starting = sum(1 for a in register.allocations if not a.base and a.start and today <= a.start <= horizon)
    day_off = next_day_off(register, today)
    off = f"next day off {day_off}" if day_off else "no day off ahead"
    return (f"Capacity register {name}: {members} members with a base allocation, {starting} periods starting in "
            f"the next {LOOKAHEAD_DAYS} days, {off}.")


@dataclass(frozen=True)
class Segment:
    start: date
    end: date
    days: int
    percent: int


@dataclass(frozen=True)
class MemberAvailability:
    member: str
    segments: tuple[Segment, ...]

    @property
    def hundredths(self) -> int:
        """Person-days × 100, kept whole to avoid rounding."""
        return sum(s.days * s.percent for s in self.segments)


@dataclass(frozen=True)
class Availability:
    start: date
    end: date
    working_days: int
    days_off: tuple[tuple[date, CalendarDay], ...]
    events: tuple[tuple[date, CalendarDay], ...]
    members: tuple[MemberAvailability, ...]

    @property
    def counted_days(self) -> int:
        return self.working_days - len(self.days_off)

    @property
    def hundredths(self) -> int:
        return sum(m.hundredths for m in self.members)


def _calendar_on(register: Register, day: date, kinds: tuple[str, ...]) -> Optional[CalendarDay]:
    for entry in register.calendar:
        if entry.kind in kinds and entry.start and entry.start <= day <= (entry.end or entry.start):
            return entry
    return None


def allocation_on(register: Register, member: str, day: date) -> int:
    """The member's allocation that day: a period covering it, else the latest base row in effect, else 0."""
    rows = [a for a in register.allocations if a.member == member and a.start and a.percent is not None]
    for a in rows:
        if not a.base and a.end and a.start <= day <= a.end:
            return a.percent
    bases = [a for a in rows if a.base and a.start <= day]
    return max(bases, key=lambda a: a.start).percent if bases else 0


def _segments(register: Register, member: str, days: list[date]) -> tuple[Segment, ...]:
    segments: list[Segment] = []
    for day in days:
        percent = allocation_on(register, member, day)
        last = segments[-1] if segments else None
        if last and last.percent == percent:
            segments[-1] = Segment(last.start, day, last.days + 1, percent)
        else:
            segments.append(Segment(day, day, 1, percent))
    return tuple(segments)


def available(register: Register, start: date, end: date, member: Optional[str] = None) -> Availability:
    """Person-days per member between start and end, both included."""
    working = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    working = [d for d in working if WEEKDAYS[d.weekday()] in register.working_days]
    days_off = tuple((d, e) for d in working for e in [_calendar_on(register, d, DAYS_OFF)] if e)
    off = {d for d, _ in days_off}
    counted = [d for d in working if d not in off]
    events = tuple((d, e) for d in counted for e in [_calendar_on(register, d, ("event",))] if e)
    names = [member] if member else list(dict.fromkeys(a.member for a in register.allocations))
    members = tuple(MemberAvailability(m, _segments(register, m, counted)) for m in names)
    return Availability(start, end, len(working), days_off, events, members)


def person_days(hundredths: int) -> str:
    whole, rest = divmod(hundredths, 100)
    return f"{whole}" if not rest else f"{whole}.{rest:02d}".rstrip("0")


def _days_list(items: tuple[tuple[date, CalendarDay], ...]) -> str:
    return "; ".join(f"{d} {e.kind} ({e.description})" for d, e in items) or "none"


def report(result: Availability, working_days: tuple[str, ...]) -> str:
    lines = [f"Period: {result.start} to {result.end}",
             f"Working days ({', '.join(working_days)}): {result.working_days}",
             f"Days off excluded: {len(result.days_off)}: {_days_list(result.days_off)}",
             f"Events, counted as working days: {_days_list(result.events)}",
             f"Counted days: {result.counted_days}", ""]
    for m in result.members:
        lines.append(m.member)
        for s in m.segments:
            lines.append(f"  {s.start} to {s.end}: {s.days} days at {s.percent}% = "
                         f"{person_days(s.days * s.percent)}")
        lines.append(f"  person-days: {person_days(m.hundredths)}")
    lines += ["", f"Total: {person_days(result.hundredths)} person-days"]
    return "\n".join(lines)


def _available_cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="capacity_register.py available")
    parser.add_argument("file", type=Path)
    parser.add_argument("--from", dest="start", required=True, type=date.fromisoformat)
    parser.add_argument("--to", dest="end", required=True, type=date.fromisoformat)
    parser.add_argument("--member")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2
    if args.end < args.start:
        print(f"--to {args.end} is before --from {args.start}", file=sys.stderr)
        return 2
    try:
        text = args.file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"cannot read {args.file}: {exc}", file=sys.stderr)
        return 2
    register, errors = parse(text)
    if errors:
        print(f"{args.file} is not a valid capacity register:", file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
        return 2
    if args.member and all(a.member != args.member for a in register.allocations):
        print(f"{args.member} has no allocation rows in {args.file}", file=sys.stderr)
        return 2
    print(report(available(register, args.start, args.end, args.member), register.working_days))
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "available":
        return _available_cli(argv[1:])
    return md.validate_cli(argv, "capacity_register.py", validate)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
