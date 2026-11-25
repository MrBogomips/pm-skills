#!/usr/bin/env python3
"""Parse and validate a gate register (GATES.md): phase gates, their criteria and the outcomes decided.

The format is specified in shared/registers/gates.md. Python 3 standard library only.

Usage:
    gates_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# Gates"
SECTIONS = ("## Gates", "## Criteria", "## Outcomes")
COLUMNS = {
    "## Gates": ("ID", "Gate", "Milestone", "Planned", "Status"),
    "## Criteria": ("Gate", "#", "Criterion"),
    "## Outcomes": ("Gate", "Date", "Outcome", "Decided by", "Conditions", "Review"),
}
ID_RE = re.compile(r"^G-[0-9]{3,}$")
MILESTONE_RE = re.compile(r"^A-[0-9]{3,}$")
STATUSES = ("open", "passed", "stopped")
OUTCOMES = ("go", "go with conditions", "hold", "stop")
NEEDS_CONDITIONS = ("go with conditions", "hold")
FINAL = ("go", "stop")
STATUS_AFTER = {"go": "passed", "go with conditions": "passed", "hold": "open", "stop": "stopped"}
SKILL = "/pm-skills:phase-gate-review"


@dataclass(frozen=True)
class Gate:
    id: str
    name: str
    milestone: str
    planned: Optional[date]
    status: str
    line: int


@dataclass(frozen=True)
class Criterion:
    gate: str
    number: int
    text: str
    line: int


@dataclass(frozen=True)
class Outcome:
    gate: str
    date: Optional[date]
    outcome: str
    decided_by: str
    conditions: str
    review: str
    line: int


@dataclass(frozen=True)
class Register:
    gates: tuple[Gate, ...]
    criteria: tuple[Criterion, ...]
    outcomes: tuple[Outcome, ...]


@dataclass
class _Scanner:
    errors: list[str] = field(default_factory=list)
    title_seen: bool = False
    current: Optional[str] = None
    seen: dict[str, int] = field(default_factory=dict)
    tables: dict[str, md.Table] = field(default_factory=lambda: {s: md.Table(COLUMNS[s]) for s in SECTIONS})
    with_table: set[str] = field(default_factory=set)

    def scan(self, text: str) -> int:
        number = 0
        for number, raw in enumerate(text.splitlines(), start=1):
            self._line(number, raw.strip())
        return max(number, 1)

    def _line(self, number: int, line: str) -> None:
        if not line:
            if self.current is not None:
                self.tables[self.current].close()
        elif line == TITLE and not self.title_seen and self.current is None:
            self.title_seen = True
        elif line in SECTIONS:
            self._section(number, line)
        elif line.startswith("|") and self.current is not None and self.tables[self.current].open:
            self.with_table.add(self.current)
            self.tables[self.current].feed(number, line, self.errors)
        else:
            self.errors.append(f"line {number}: unexpected content: only the title, the sections "
                               f"{', '.join(SECTIONS)} and their tables are allowed")

    def _section(self, number: int, line: str) -> None:
        if line in self.seen:
            self.errors.append(f"line {number}: duplicate section '{line}' (first on line {self.seen[line]})")
        elif any(SECTIONS.index(s) > SECTIONS.index(line) for s in self.seen):
            self.errors.append(f"line {number}: section '{line}' is out of order: the sections are "
                               f"{', '.join(SECTIONS)}, in this order")
        self.seen.setdefault(line, number)
        self.current = line


def _gate(row: md.Row, errors: list[str]) -> Gate:
    c, n = row.cells, row.line
    if not ID_RE.match(c["ID"]):
        errors.append(f"line {n}: ID '{c['ID']}' must be G- followed by at least three digits (G-001)")
    if not c["Gate"]:
        errors.append(f"line {n}: Gate is empty: name the gate")
    if c["Milestone"] and not MILESTONE_RE.match(c["Milestone"]):
        errors.append(f"line {n}: Milestone '{c['Milestone']}' must be empty or a schedule activity ID (A-004)")
    planned = md.parse_date(c["Planned"], n, "Planned", errors) if c["Planned"] else None
    if c["Status"] not in STATUSES:
        errors.append(f"line {n}: Status '{c['Status']}' must be one of: {', '.join(STATUSES)}")
    md.check_contacts(n, "Gate", c["Gate"], errors)
    return Gate(c["ID"], c["Gate"], c["Milestone"], planned, c["Status"], n)


def _criterion(row: md.Row, errors: list[str]) -> Criterion:
    c, n = row.cells, row.line
    number = int(c["#"]) if md.is_number(c["#"]) else 0
    if number < 1:
        errors.append(f"line {n}: # '{c['#']}' must be a whole number from 1, in ASCII digits")
    if not c["Criterion"]:
        errors.append(f"line {n}: Criterion is empty")
    md.check_contacts(n, "Criterion", c["Criterion"], errors, phone=False)
    return Criterion(c["Gate"], number, c["Criterion"], n)


def _outcome(row: md.Row, errors: list[str]) -> Outcome:
    c, n = row.cells, row.line
    if c["Date"]:
        when = md.parse_date(c["Date"], n, "Date", errors)
    else:
        when = None
        errors.append(f"line {n}: Date is empty: the day the outcome was decided")
    if c["Outcome"] not in OUTCOMES:
        errors.append(f"line {n}: Outcome '{c['Outcome']}' must be one of: {', '.join(OUTCOMES)}")
    if not c["Decided by"]:
        errors.append(f"line {n}: Decided by is empty: the role or body that took the decision")
    if c["Outcome"] in NEEDS_CONDITIONS and not c["Conditions"]:
        errors.append(f"line {n}: Conditions are required for '{c['Outcome']}': what must happen, by when")
    md.check_contacts(n, "Decided by", c["Decided by"], errors)
    md.check_contacts(n, "Conditions", c["Conditions"], errors, phone=False)
    return Outcome(c["Gate"], when, c["Outcome"], c["Decided by"], c["Conditions"], c["Review"], n)


def _check_references(register: Register, errors: list[str]) -> None:
    first: dict[str, int] = {}
    for g in register.gates:
        if g.id in first:
            errors.append(f"line {g.line}: duplicate ID '{g.id}' (first on line {first[g.id]})")
        first.setdefault(g.id, g.line)
    for item in register.criteria + register.outcomes:
        if item.gate not in first:
            errors.append(f"line {item.line}: unknown gate '{item.gate}': add it to '## Gates' first")
    numbers: dict[tuple[str, int], int] = {}
    for c in register.criteria:
        key = (c.gate, c.number)
        if c.number and key in numbers:
            errors.append(f"line {c.line}: duplicate criterion {c.number} of {c.gate} (first on line {numbers[key]})")
        numbers.setdefault(key, c.line)
    with_criteria = {c.gate for c in register.criteria}
    for g in register.gates:
        if g.id not in with_criteria:
            errors.append(f"line {g.line}: {g.id} has no criteria: add at least one under '## Criteria'")


def _check_history(register: Register, errors: list[str]) -> None:
    last: dict[str, Outcome] = {}
    for o in register.outcomes:
        previous = last.get(o.gate)
        if previous is not None:
            if previous.outcome in FINAL:
                errors.append(f"line {o.line}: no outcome may follow '{previous.outcome}' for {o.gate} "
                              f"(line {previous.line}): open a new gate instead")
            if previous.date and o.date and o.date < previous.date:
                errors.append(f"line {o.line}: {o.gate} outcome on {o.date} breaks the date order "
                              f"(previous on {previous.date})")
        last[o.gate] = o
    for g in register.gates:
        if g.status not in STATUSES:
            continue
        outcome = last.get(g.id)
        expected = STATUS_AFTER.get(outcome.outcome, g.status) if outcome else "open"
        if g.status != expected:
            why = f"the last outcome is '{outcome.outcome}'" if outcome else "it has no outcome"
            errors.append(f"line {g.line}: Status '{g.status}' must be '{expected}': {why}")


def parse(text: str) -> tuple[Register, list[str]]:
    scanner = _Scanner()
    last = scanner.scan(text)
    errors = scanner.errors
    if not scanner.title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    for section in SECTIONS:
        if section not in scanner.seen:
            errors.append(f"line {last}: missing section '{section}'")
        elif section not in scanner.with_table:
            errors.append(f"line {scanner.seen[section]}: section '{section}' has no table "
                          f"({' | '.join(COLUMNS[section])})")
    register = Register(
        tuple(_gate(r, errors) for r in scanner.tables["## Gates"].rows),
        tuple(_criterion(r, errors) for r in scanner.tables["## Criteria"].rows),
        tuple(_outcome(r, errors) for r in scanner.tables["## Outcomes"].rows),
    )
    _check_references(register, errors)
    _check_history(register, errors)
    return register, md.sort_errors(errors)


def validate(text: str) -> list[str]:
    return parse(text)[1]


def _counts(gates: tuple[Gate, ...]) -> str:
    parts = [f"{sum(1 for g in gates if g.status == s)} {s}" for s in ("passed", "open", "stopped")]
    return ", ".join(p for p in parts if not p.startswith("0 "))


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Gate register {name} is declared but missing: run {SKILL} to create it."
    register, errors = parse(text)
    if errors:
        return f"Gate register {name} has {md.count_of(len(errors), 'validation error')}: run {SKILL} to fix them."
    if not register.gates:
        return f"Gate register {name}: no gates yet."
    head = f"Gate register {name}: {md.count_of(len(register.gates), 'gate')} ({_counts(register.gates)})"
    open_gates = [g for g in register.gates if g.status == "open"]
    if not open_gates:
        return f"{head}, no open gate."
    planned = sorted((g for g in open_gates if g.planned), key=lambda g: g.planned)
    if not planned:
        return f"{head}, no planned date for the open gates."
    nxt = planned[0]
    if nxt.planned < today:
        return f"{head}, next {nxt.id} planned {nxt.planned}, past its planned date: run {SKILL}."
    return f"{head}, next {nxt.id} planned {nxt.planned}."


if __name__ == "__main__":
    sys.exit(md.validate_cli(sys.argv[1:], "gates_register.py", validate))
