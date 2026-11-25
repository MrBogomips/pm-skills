#!/usr/bin/env python3
"""Parse and validate a flow snapshot (the transition history of work items), and the flow helpers shared by
flow_metrics.py, forecast.py and dora.py.

The format is specified in shared/registers/flow-snapshot.md. Python 3 standard library only.

Usage:
    flow_data.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
"""
from __future__ import annotations

import csv
import io
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional, Sequence

HEADER = ("item", "type", "state", "entered_at")
TIMESTAMP_RE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})"
                          r"(?:[T ]([0-9]{2}):([0-9]{2})(?::([0-9]{2})(?:\.([0-9]{1,6}))?)?"
                          r"(Z|([+-])([0-9]{2}):([0-9]{2}))?)?")
NAME_DATE_RE = re.compile(r"^([0-9]{4}-[0-9]{2}-[0-9]{2})-flow-snapshot\.csv$")
PERCENTILES = (50, 85, 95)
WEEK_DAYS = 7
MAX_WEEKS = 1000
MICROSECOND_DIGITS = 6


@dataclass(frozen=True)
class Transition:
    item: str
    type: str
    state: str
    entered_at: datetime
    line: int


@dataclass(frozen=True)
class Workflow:
    """Which states mean work in progress (all of them) and which mean finished."""
    started: frozenset[str]
    finished: frozenset[str]

    @staticmethod
    def parse(started: str, finished: str) -> "Workflow":
        s, f = _states(started), _states(finished)
        if not s or not f:
            raise ValueError("--started and --finished each need at least one state")
        both = s & f
        if both:
            raise ValueError(f"a state cannot be both started and finished: {', '.join(sorted(both))}")
        return Workflow(s, f)


@dataclass(frozen=True)
class Item:
    key: str
    type: str
    transitions: tuple[Transition, ...]

    def started_on(self, wf: Workflow) -> Optional[date]:
        """The day the item first entered a started state."""
        return next((t.entered_at.date() for t in self.transitions if t.state in wf.started), None)

    def finished_on(self, wf: Workflow) -> Optional[date]:
        """The day of the first finished state after the first start (or the first finish, if never started).
        Reopening and finishing again does not move it."""
        start = next((t.entered_at for t in self.transitions if t.state in wf.started), None)
        return next((t.entered_at.date() for t in self.transitions
                     if t.state in wf.finished and (start is None or t.entered_at >= start)), None)

    def cycle_time(self, wf: Workflow) -> Optional[int]:
        """Calendar days from the first start to the first finish after it, both days counted."""
        start, finish = self.started_on(wf), self.finished_on(wf)
        return (finish - start).days + 1 if start and finish else None

    def state_on(self, day: date) -> Optional[str]:
        """The state at the end of the day."""
        states = [t.state for t in self.transitions if t.entered_at.date() <= day]
        return states[-1] if states else None

    def in_progress_on(self, wf: Workflow, day: date) -> bool:
        return self.state_on(day) in wf.started

    def reopened_on(self, wf: Workflow, day: date) -> bool:
        finish = self.finished_on(wf)
        return finish is not None and finish <= day and self.state_on(day) not in wf.finished

    def age_on(self, wf: Workflow, day: date) -> Optional[int]:
        """Calendar days from the first start to the day, both counted."""
        start = self.started_on(wf)
        return (day - start).days + 1 if start and start <= day else None


@dataclass(frozen=True)
class Week:
    start: date
    end: date


def _states(value: str) -> frozenset[str]:
    return frozenset(s.strip() for s in value.split(",") if s.strip())


def parse_timestamp(value: str) -> Optional[datetime]:
    """An ISO 8601 date or date-time; an offset is converted to UTC and dropped. None when invalid.

    Built from the parts of the match rather than with datetime.fromisoformat, which on Python 3.9 accepts only
    three or six fractional digits: the result is the same on every Python version."""
    match = TIMESTAMP_RE.fullmatch(value)
    if not match:
        return None
    year, month, day, hour, minute, second, fraction, zone, sign, zone_hours, zone_minutes = match.groups()
    try:
        parsed = datetime(int(year), int(month), int(day), int(hour or 0), int(minute or 0), int(second or 0),
                          int((fraction or "").ljust(MICROSECOND_DIGITS, "0")))
        if zone is None:
            return parsed
        offset = timedelta(0)
        if zone != "Z":
            if int(zone_minutes) > 59:
                return None
            offset = timedelta(hours=int(zone_hours), minutes=int(zone_minutes)) * (-1 if sign == "-" else 1)
        return parsed.replace(tzinfo=timezone(offset)).astimezone(timezone.utc).replace(tzinfo=None)
    except (ValueError, OverflowError):
        return None


def read_csv(text: str, header: tuple[str, ...], errors: list[str]) -> list[tuple[int, list[str]]]:
    """The data rows with their line numbers, after checking the exact header and the number of cells.
    A leading UTF-8 byte order mark is ignored; a CSV the reader cannot parse is reported as an error."""
    reader = csv.reader(io.StringIO(text.lstrip("\ufeff")))
    rows: list[tuple[int, list[str]]] = []
    try:
        first = next(reader, None)
        if first is None or tuple(c.strip() for c in first) != header:
            errors.append(f"line 1: the header must be exactly '{','.join(header)}', with no other column")
            return []
        for cells in reader:
            if not any(c.strip() for c in cells):
                continue
            if len(cells) != len(header):
                errors.append(f"line {reader.line_num}: {len(cells)} cells, expected {len(header)} cells")
                continue
            rows.append((reader.line_num, [c.strip() for c in cells]))
    except csv.Error as exc:
        errors.append(f"line {max(reader.line_num, 1)}: {exc}")
    return rows


def _transition(number: int, cells: list[str], errors: list[str]) -> Optional[Transition]:
    values = dict(zip(HEADER, cells))
    empty = [name for name in HEADER if not values[name]]
    if empty:
        errors.append(f"line {number}: empty {', '.join(empty)}")
        return None
    entered = parse_timestamp(values["entered_at"])
    if entered is None:
        errors.append(f"line {number}: entered_at '{values['entered_at']}' is not an ISO 8601 date "
                      f"(YYYY-MM-DD) or date-time (YYYY-MM-DDTHH:MM[:SS][Z|+HH:MM])")
        return None
    return Transition(values["item"], values["type"], values["state"], entered, number)


def _check_items(transitions: list[Transition], errors: list[str]) -> None:
    seen: set[tuple[str, str, str, datetime]] = set()
    last: dict[str, Transition] = {}
    for t in transitions:
        key = (t.item, t.type, t.state, t.entered_at)
        if key in seen:
            errors.append(f"line {t.line}: duplicate row")
        seen.add(key)
        previous = last.get(t.item)
        if previous and previous.type != t.type:
            errors.append(f"line {t.line}: {t.item} has type '{t.type}' here and '{previous.type}' "
                          f"on line {previous.line}")
        if previous and t.entered_at < previous.entered_at:
            errors.append(f"line {t.line}: {t.item} enters '{t.state}' before its previous transition "
                          f"on line {previous.line}: rows of an item go in time order")
        last[t.item] = t


def parse(text: str) -> tuple[tuple[Transition, ...], list[str]]:
    errors: list[str] = []
    transitions = [t for number, cells in read_csv(text, HEADER, errors)
                   for t in [_transition(number, cells, errors)] if t]
    _check_items(transitions, errors)
    return tuple(transitions), sorted(errors, key=lambda e: int(e.split(":", 1)[0].split()[1]))


def validate(text: str) -> list[str]:
    return parse(text)[1]


def items(transitions: Iterable[Transition]) -> tuple[Item, ...]:
    """Transitions grouped by item, in order of first appearance."""
    grouped: dict[str, list[Transition]] = {}
    for t in transitions:
        grouped.setdefault(t.item, []).append(t)
    return tuple(Item(key, ts[0].type, tuple(ts)) for key, ts in grouped.items())


def percentile(values: Sequence[float], p: int) -> float:
    """Nearest-rank percentile: the value at rank ceil(p/100 * n) of the values sorted ascending (p from 1 to 100,
    rank computed in integers so that no rounding error moves it)."""
    if not values:
        raise ValueError("percentile of no values")
    if not 0 < p <= 100:
        raise ValueError(f"percentile {p} is not from 1 to 100")
    ordered = sorted(values)
    rank = max(1, -(-p * len(ordered) // 100))
    return ordered[rank - 1]


def weeks_ending(end: date, earliest: date) -> tuple[Week, ...]:
    """Whole 7-day weeks, the last ending on end, none starting before earliest."""
    count = ((end - earliest).days + 1) // WEEK_DAYS
    first = end - timedelta(days=count * WEEK_DAYS - 1)
    return tuple(Week(first + timedelta(days=i * WEEK_DAYS), first + timedelta(days=(i + 1) * WEEK_DAYS - 1))
                 for i in range(count))


def throughput(items_: Iterable[Item], wf: Workflow, weeks: Sequence[Week]) -> tuple[int, ...]:
    """Items finished in each week, zero weeks included."""
    finishes = [f for f in (i.finished_on(wf) for i in items_) if f]
    return tuple(sum(1 for f in finishes if w.start <= f <= w.end) for w in weeks)


def date_from_name(path: Path) -> Optional[date]:
    """The snapshot date in a name such as 2026-12-07-flow-snapshot.csv."""
    match = NAME_DATE_RE.match(path.name)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


class DataError(Exception):
    """The file was read but holds invalid data (exit 1)."""


def load(path: Path) -> tuple[Item, ...]:
    """Read and validate a snapshot. OSError when unreadable, DataError (with the errors) when invalid."""
    transitions, errors = parse(path.read_text(encoding="utf-8"))
    if errors:
        raise DataError("\n".join([f"{path} is not a valid flow snapshot:", *errors]))
    return items(transitions)


def snapshot_today(path: Path, found: tuple[Item, ...], given: Optional[date]) -> tuple[date, str]:
    """The day the snapshot describes: given, else the date in the file name, else its latest transition."""
    if given:
        return given, "given"
    named = date_from_name(path)
    if named:
        return named, "from the file name"
    latest = max((t.entered_at.date() for i in found for t in i.transitions), default=date.today())
    return latest, "the latest transition in the file"


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] != "validate":
        print("usage: flow_data.py validate FILE", file=sys.stderr)
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
    sys.exit(main(sys.argv[1:]))
