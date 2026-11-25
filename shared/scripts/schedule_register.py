#!/usr/bin/env python3
"""Parse and validate a schedule register (SCHEDULE.md), and run the critical path method over its plan.

The format is specified in shared/registers/schedule.md. Python 3 standard library only.

Usage:
    schedule_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
    schedule_register.py cpm FILE [--activities CSV] [--capacity CAPACITY.md] [--start YYYY-MM-DD]
                                  [--status-date YYYY-MM-DD] [--baseline B-NN|latest]
        print early and late dates, total float, critical paths and the variance against a baseline;
        exit 1 on invalid data, 2 on a usage or I/O error
"""
from __future__ import annotations

import csv
import io
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# Schedule"
SOURCE = "Source:"
REGISTER_SOURCE = "register"
ACTIVITIES = "## Activities"
ACTIVITY_COLUMNS = ("ID", "Activity", "Duration", "Predecessors", "Start", "Finish", "Progress")
CSV_COLUMNS = tuple(c.lower() for c in ACTIVITY_COLUMNS)
BASELINE_COLUMNS = ("ID", "Activity", "Start", "Finish")
BASELINE_KEYS = ("Approved", "Approved by", "Change")
ID_RE = re.compile(r"^A-[0-9]{3,}$")
BASELINE_RE = re.compile(r"^## Baseline (B-[0-9]{2,})\s+(\S.*)$")
BASELINE_ID_RE = re.compile(r"^B-[0-9]{2,}$")
PREDECESSOR_RE = re.compile(r"^(A-[0-9]{3,})(?:\s+(FS|SS|FF)(?:([+-])([0-9]{1,15}))?)?$")
CHANGE_RE = re.compile(r"^CR-[0-9]{3,}$")
SKILL = "/pm-skills:schedule-check"


@dataclass(frozen=True)
class Link:
    pred: str
    kind: str
    lag: int


@dataclass(frozen=True)
class Activity:
    id: str
    name: str
    duration: int
    links: tuple[Link, ...]
    start: Optional[date]
    finish: Optional[date]
    progress: int
    line: int

    @property
    def milestone(self) -> bool:
        return self.duration == 0


@dataclass(frozen=True)
class BaselineRow:
    id: str
    name: str
    start: Optional[date]
    finish: Optional[date]
    line: int


@dataclass(frozen=True)
class Baseline:
    id: str
    name: str
    approved: Optional[date]
    approved_by: str
    change: str
    rows: tuple[BaselineRow, ...]
    line: int


@dataclass(frozen=True)
class Register:
    source: str
    activities: tuple[Activity, ...]
    baselines: tuple[Baseline, ...]
    has_activities: bool


# --- activities ---------------------------------------------------------------------------------------------------

def _links(value: str, n: int, errors: list[str]) -> tuple[Link, ...]:
    if not value:
        return ()
    links = []
    for item in md.split_list(value):
        match = PREDECESSOR_RE.match(item)
        if not match:
            errors.append(f"line {n}: predecessor '{item}' must be an activity ID, optionally followed by FS, SS "
                          "or FF and a lag such as +2 (for example 'A-002 SS+5')")
            continue
        lag = int(match.group(4) or 0) * (-1 if match.group(3) == "-" else 1)
        links.append(Link(match.group(1), match.group(2) or "FS", lag))
    return tuple(links)


def _whole(value: str, n: int, what: str, maximum: Optional[int], errors: list[str]) -> int:
    if md.is_number(value) and (maximum is None or int(value) <= maximum):
        return int(value)
    limit = f" from 0 to {maximum}, without %" if maximum is not None else ""
    errors.append(f"line {n}: {what} '{value}' must be a whole number{limit}")
    return 0


def _optional_date(value: str, n: int, what: str, errors: list[str]) -> Optional[date]:
    return md.parse_date(value, n, what, errors) if value else None


def activity_from_cells(c: dict[str, str], n: int, errors: list[str]) -> Activity:
    """One activity from a table row or a CSV row, keyed by the register's column names."""
    if not ID_RE.match(c["ID"]):
        errors.append(f"line {n}: ID '{c['ID']}' must be A- and at least three digits")
    if not c["Activity"]:
        errors.append(f"line {n}: Activity is empty")
    md.check_contacts(n, "Activity", c["Activity"], errors)
    duration = _whole(c["Duration"], n, "Duration", None, errors)
    start = _optional_date(c["Start"], n, "Start", errors)
    finish = _optional_date(c["Finish"], n, "Finish", errors)
    progress = _whole(c["Progress"], n, "Progress", 100, errors)
    if start and finish and finish < start:
        errors.append(f"line {n}: Finish {finish} is before Start {start}")
    activity = Activity(c["ID"], c["Activity"], duration, _links(c["Predecessors"], n, errors), start, finish,
                        progress, n)
    if md.is_number(c["Duration"]) and activity.milestone:
        _milestone(activity, errors)
    return activity


def _milestone(a: Activity, errors: list[str]) -> None:
    if a.progress not in (0, 100):
        errors.append(f"line {a.line}: a milestone (Duration 0) has Progress 0 or 100, not {a.progress}")
    if a.start and a.finish and a.start != a.finish:
        errors.append(f"line {a.line}: a milestone (Duration 0) has the same Start and Finish")


def check_network(activities: tuple[Activity, ...], errors: list[str]) -> None:
    """Duplicate IDs, unknown, self and repeated predecessors, and cycles."""
    first: dict[str, int] = {}
    for a in activities:
        if a.id in first:
            errors.append(f"line {a.line}: duplicate ID '{a.id}' (first on line {first[a.id]})")
        first.setdefault(a.id, a.line)
    for a in activities:
        seen: set[str] = set()
        for link in a.links:
            if link.pred == a.id:
                errors.append(f"line {a.line}: {a.id} depends on itself")
            elif link.pred not in first:
                errors.append(f"line {a.line}: unknown predecessor '{link.pred}'")
            elif link.pred in seen:
                errors.append(f"line {a.line}: predecessor '{link.pred}' is named twice")
            seen.add(link.pred)
    for cycle in find_cycles(activities):
        errors.append(f"line {first[cycle[0]]}: the dependencies form a cycle: {' → '.join(cycle + (cycle[0],))}")


def successors(activities: tuple[Activity, ...]) -> dict[str, list[str]]:
    ids = {a.id for a in activities}
    result: dict[str, list[str]] = {a.id: [] for a in activities}
    for a in activities:
        for link in a.links:
            if link.pred in ids and link.pred != a.id and a.id not in result[link.pred]:
                result[link.pred].append(a.id)
    return result


def find_cycles(activities: tuple[Activity, ...]) -> list[tuple[str, ...]]:
    """Each distinct cycle once, from predecessor to successor, starting at its first activity in file order."""
    following = successors(activities)
    order = {a.id: i for i, a in enumerate(activities)}
    state: dict[str, int] = {}  # 1 on the stack, 2 done
    found: dict[frozenset[str], tuple[str, ...]] = {}
    for root in following:
        if state.get(root):
            continue
        stack: list[tuple[str, int]] = [(root, 0)]
        path: list[str] = [root]
        state[root] = 1
        while stack:
            node, index = stack[-1]
            if index < len(following[node]):
                stack[-1] = (node, index + 1)
                nxt = following[node][index]
                if state.get(nxt) == 1:
                    cycle = path[path.index(nxt):]
                    pivot = min(range(len(cycle)), key=lambda i: order[cycle[i]])
                    found.setdefault(frozenset(cycle), tuple(cycle[pivot:] + cycle[:pivot]))
                elif not state.get(nxt):
                    state[nxt] = 1
                    stack.append((nxt, 0))
                    path.append(nxt)
            else:
                state[node] = 2
                stack.pop()
                path.pop()
    return sorted(found.values(), key=lambda c: order[c[0]])


# --- register -----------------------------------------------------------------------------------------------------

@dataclass
class _BaselineDraft:
    id: str
    name: str
    line: int
    entries: dict[str, tuple[str, int]] = field(default_factory=dict)
    table: md.Table = field(default_factory=lambda: md.Table(BASELINE_COLUMNS))
    seen_table: bool = False


class _Scanner:
    """Line-by-line state machine: preamble -> Activities -> baselines."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.title_seen = False
        self.source: Optional[str] = None
        self.in_activities = False
        self.activities_seen = False
        self.activities = md.Table(ACTIVITY_COLUMNS)
        self.activities_table_seen = False
        self.baselines: list[_BaselineDraft] = []

    def scan(self, text: str) -> int:
        last = 0
        for number, raw in enumerate(text.splitlines(), start=1):
            last = number
            self._line(number, raw.strip())
        return last

    def _table(self) -> Optional[md.Table]:
        if self.baselines:
            return self.baselines[-1].table
        return self.activities if self.in_activities else None

    def _line(self, number: int, line: str) -> None:
        table = self._table()
        if not line:
            if table is not None and table.state != "header":
                table.close()
        elif line == TITLE and not self.title_seen and not self._in_sections():
            self.title_seen = True
        elif line.startswith(SOURCE) and not self._in_sections() and self.source is None:
            self.source = line[len(SOURCE):].strip()
            if not self.source:
                self.errors.append(f"line {number}: Source is empty: 'register' or the name of a schedule tool")
        elif line.startswith("## "):
            self._section(number, line)
        elif line.startswith("|") and table is not None and table.open:
            self._mark_table()
            table.feed(number, line, self.errors)
        elif self.baselines and not self.baselines[-1].seen_table and md.entry(line):
            self._entry(number, *md.entry(line))
        else:
            self.errors.append(f"line {number}: unexpected content: only the title, '{SOURCE}', the sections, "
                               "baseline entries and the tables are allowed")

    def _in_sections(self) -> bool:
        return self.in_activities or bool(self.baselines)

    def _mark_table(self) -> None:
        if self.baselines:
            self.baselines[-1].seen_table = True
        else:
            self.activities_table_seen = True

    def _section(self, number: int, line: str) -> None:
        match = BASELINE_RE.match(line)
        if line == ACTIVITIES and not self._in_sections():
            self.in_activities = self.activities_seen = True
        elif match:
            self.baselines.append(_BaselineDraft(match.group(1), match.group(2).strip(), number))
        else:
            self.errors.append(f"line {number}: unexpected section '{line}': the sections are '{ACTIVITIES}' "
                               "first, then '## Baseline B-NN <name>' sections")

    def _entry(self, number: int, key: str, value: str) -> None:
        draft = self.baselines[-1]
        if key not in BASELINE_KEYS:
            self.errors.append(f"line {number}: unknown entry '{key}'; the entries are: {', '.join(BASELINE_KEYS)}")
        elif key in draft.entries:
            self.errors.append(f"line {number}: '{key}' is already on line {draft.entries[key][1]}")
        elif not value:
            self.errors.append(f"line {number}: '{key}' is empty")
        else:
            draft.entries[key] = (value, number)
            md.check_contacts(number, key, value, self.errors, phone=key != "Approved")


def _baseline_row(row: md.Row, errors: list[str]) -> BaselineRow:
    c, n = row.cells, row.line
    if not ID_RE.match(c["ID"]):
        errors.append(f"line {n}: ID '{c['ID']}' must be A- and at least three digits")
    if not c["Activity"]:
        errors.append(f"line {n}: Activity is empty")
    md.check_contacts(n, "Activity", c["Activity"], errors)
    start = md.parse_date(c["Start"], n, "Start", errors) if c["Start"] else _required(n, "Start", errors)
    finish = md.parse_date(c["Finish"], n, "Finish", errors) if c["Finish"] else _required(n, "Finish", errors)
    if start and finish and finish < start:
        errors.append(f"line {n}: Finish {finish} is before Start {start}")
    return BaselineRow(c["ID"], c["Activity"], start, finish, n)


def _required(n: int, what: str, errors: list[str]) -> None:
    errors.append(f"line {n}: {what} is required in a baseline")
    return None


def _baseline(draft: _BaselineDraft, last: int, errors: list[str]) -> Baseline:
    for key in ("Approved", "Approved by"):
        if key not in draft.entries:
            errors.append(f"line {draft.line}: {draft.id} needs '- {key}:'")
    approved = None
    if "Approved" in draft.entries:
        value, n = draft.entries["Approved"]
        approved = md.parse_date(value, n, "Approved", errors)
    change = draft.entries.get("Change", ("", 0))
    if change[0] and not CHANGE_RE.match(change[0]):
        errors.append(f"line {change[1]}: Change '{change[0]}' must be one change request ID (CR-NNN)")
    if not draft.seen_table:
        errors.append(f"line {last}: baseline {draft.id} has no table")
    elif not draft.table.rows:
        errors.append(f"line {draft.line}: baseline {draft.id} has no rows: a baseline records the planned start "
                      "and finish of the activities")
    rows = tuple(_baseline_row(row, errors) for row in draft.table.rows)
    first: dict[str, int] = {}
    for row in rows:
        if row.id in first:
            errors.append(f"line {row.line}: duplicate ID '{row.id}' in {draft.id} (first on line {first[row.id]})")
        first.setdefault(row.id, row.line)
    return Baseline(draft.id, draft.name, approved, draft.entries.get("Approved by", ("", 0))[0], change[0], rows,
                    draft.line)


def _baseline_order(baselines: tuple[Baseline, ...], errors: list[str]) -> None:
    seen: dict[int, int] = {}
    previous: Optional[Baseline] = None
    for b in baselines:
        number = int(b.id[2:])
        if number in seen:
            errors.append(f"line {b.line}: duplicate baseline '{b.id}' (first on line {seen[number]})")
        elif previous and number < int(previous.id[2:]):
            errors.append(f"line {b.line}: {b.id} comes after {previous.id}: keep baselines in increasing order")
        seen.setdefault(number, b.line)
        if previous and b.approved and previous.approved and b.approved < previous.approved:
            errors.append(f"line {b.line}: {b.id} approved on {b.approved}, before the approval of {previous.id} "
                          f"on {previous.approved}")
        previous = b


def parse(text: str) -> tuple[Register, list[str]]:
    scanner = _Scanner()
    last = scanner.scan(text)
    errors = scanner.errors
    if not scanner.title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    if scanner.source is None:
        errors.append(f"line 1: missing '{SOURCE}' line: 'register' or the name of a schedule tool")
    source = scanner.source or ""
    if source == REGISTER_SOURCE and not scanner.activities_seen:
        errors.append(f"line {last}: missing section '{ACTIVITIES}': the source is the register")
    elif scanner.activities_seen and not scanner.activities_table_seen:
        errors.append(f"line {last}: section '{ACTIVITIES}' has no table")
    activities = tuple(activity_from_cells(row.cells, row.line, errors) for row in scanner.activities.rows)
    check_network(activities, errors)
    baselines = tuple(_baseline(d, last, errors) for d in scanner.baselines)
    _baseline_order(baselines, errors)
    return Register(source, activities, baselines, scanner.activities_seen), md.sort_errors(errors)


def validate(text: str) -> list[str]:
    return parse(text)[1]


def parse_activities_csv(text: str) -> tuple[tuple[Activity, ...], list[str]]:
    """Activities exported from a schedule tool, as CSV with the header id,activity,...,progress."""
    errors: list[str] = []
    reader = csv.reader(io.StringIO(text.lstrip("\ufeff")))
    activities = []
    try:
        header = next(reader, None)
        if header is None or tuple(h.strip() for h in header) != CSV_COLUMNS:
            return (), [f"line 1: the header must be exactly: {','.join(CSV_COLUMNS)}"]
        for values in reader:
            n = reader.line_num
            if not any(v.strip() for v in values):
                continue
            if len(values) != len(CSV_COLUMNS):
                errors.append(f"line {n}: expected {len(CSV_COLUMNS)} fields, found {len(values)}")
                continue
            cells = dict(zip(ACTIVITY_COLUMNS, (v.strip() for v in values)))
            activities.append(activity_from_cells(cells, n, errors))
    except csv.Error as exc:
        errors.append(f"line {max(reader.line_num, 1)}: {exc}")
    result = tuple(activities)
    check_network(result, errors)
    return result, md.sort_errors(errors)


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Schedule register {name} is declared but missing: run {SKILL} to create it."
    register, errors = parse(text)
    if errors:
        return f"Schedule register {name} has {md.count_of(len(errors), 'validation error')}: run {SKILL} to fix them."
    head = f"Schedule register {name}: source {register.source}, {len(register.activities)} activities"
    if not register.baselines:
        return f"{head}, no baseline yet."
    latest = register.baselines[-1]
    return f"{head}, latest baseline {latest.id} approved {latest.approved}."


def main(argv: list[str]) -> int:
    if argv and argv[0] == "cpm":
        import schedule_cpm

        return schedule_cpm.main(argv[1:])
    return md.validate_cli(argv, "schedule_register.py", validate)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
