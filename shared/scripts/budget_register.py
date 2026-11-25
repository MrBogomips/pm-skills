#!/usr/bin/env python3
"""Parse and validate a budget register (BUDGET.md), and compute earned value figures against it.

The format is specified in shared/registers/budget.md. Amounts are Decimal. Python 3 standard library only.

Usage:
    budget_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
    budget_register.py evm FILE --status-date YYYY-MM-DD (--pv N --ev N --ac N | --data CSV) [--eac-cpi-spi]
        print CV, SV, CPI, SPI, EAC, ETC, VAC and TCPI with the working; exit 1 on invalid data, 2 on a usage
        or I/O error
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import date
from decimal import Context, Decimal
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# Budget"
CURRENCY = "Currency:"
LAST_REVIEWED = "Last reviewed:"
SECTIONS = ("## Lines", "## Rates", "## Approved changes")
REQUIRED_SECTIONS = 2
LINE_COLUMNS = ("ID", "Line", "Kind", "Amount", "From", "To")
RATE_COLUMNS = ("Role", "Rate", "Unit", "From")
CHANGE_COLUMNS = ("Date", "Line", "Amount", "Change")
LABOR, EXPENSE, CONTINGENCY, MANAGEMENT = "labor", "expense", "contingency", "management reserve"
KINDS = (LABOR, EXPENSE, CONTINGENCY, MANAGEMENT)
BAC_KINDS = (LABOR, EXPENSE)
UNITS = ("hour", "day")
ID_RE = re.compile(r"^B-[0-9]{3,}$")
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
MAX_DIGITS = 15
AMOUNT_RE = re.compile(r"[0-9]{1,%d}(\.[0-9]{1,2})?" % MAX_DIGITS)
SIGNED_RE = re.compile(r"[+-]?[0-9]{1,%d}(\.[0-9]{1,2})?" % MAX_DIGITS)
REFERENCE_RE = re.compile(r"^(CR|D)-[0-9]{3,}$")
CENT = Decimal("0.01")
# Wide enough to show any figure computed from amounts of at most MAX_DIGITS digits, ratios included.
DISPLAY = Context(prec=120)
SKILL = "/pm-skills:budget-tracker"


@dataclass(frozen=True)
class Line:
    id: str
    name: str
    kind: str
    amount: Decimal
    start: Optional[date]
    end: Optional[date]
    line: int


@dataclass(frozen=True)
class Rate:
    role: str
    rate: Decimal
    unit: str
    start: Optional[date]
    line: int


@dataclass(frozen=True)
class Change:
    day: Optional[date]
    target: str
    amount: Decimal
    reference: str
    line: int


@dataclass(frozen=True)
class Register:
    currency: str
    last_reviewed: Optional[date]
    lines: tuple[Line, ...]
    rates: tuple[Rate, ...]
    changes: tuple[Change, ...]


def money(value: Decimal) -> str:
    return str(value.quantize(CENT, context=DISPLAY))


def _amount(value: str, n: int, what: str, pattern: re.Pattern, rule: str, errors: list[str]) -> Decimal:
    if pattern.fullmatch(value):
        return Decimal(value)
    errors.append(f"line {n}: {what} '{value}' must be {rule}, at most {MAX_DIGITS} digits before the point and two "
                  "after it, a point as decimal mark and no thousands separator")
    return Decimal(0)


def _line(row: md.Row, errors: list[str]) -> Line:
    c, n = row.cells, row.line
    if not ID_RE.match(c["ID"]):
        errors.append(f"line {n}: ID '{c['ID']}' must be B- and at least three digits")
    if not c["Line"]:
        errors.append(f"line {n}: Line is empty")
    md.check_contacts(n, "Line", c["Line"], errors)
    if c["Kind"] not in KINDS:
        errors.append(f"line {n}: Kind '{c['Kind']}' must be one of: {', '.join(KINDS)}")
    amount = _amount(c["Amount"], n, "Amount", AMOUNT_RE, "a number not below zero", errors)
    start = md.parse_date(c["From"], n, "From", errors)
    end = md.parse_date(c["To"], n, "To", errors)
    if start and end and end < start:
        errors.append(f"line {n}: To {end} is before From {start}")
    return Line(c["ID"], c["Line"], c["Kind"], amount, start, end, n)


def _rate(row: md.Row, errors: list[str]) -> Rate:
    c, n = row.cells, row.line
    if not c["Role"]:
        errors.append(f"line {n}: Role is empty")
    md.check_contacts(n, "Role", c["Role"], errors)
    rate = _amount(c["Rate"], n, "Rate", AMOUNT_RE, "a number above zero", errors)
    if rate == 0 and AMOUNT_RE.fullmatch(c["Rate"]):
        errors.append(f"line {n}: Rate '{c['Rate']}' must be above zero")
    if c["Unit"] not in UNITS:
        errors.append(f"line {n}: Unit '{c['Unit']}' must be one of: {', '.join(UNITS)}")
    return Rate(c["Role"], rate, c["Unit"], md.parse_date(c["From"], n, "From", errors), n)


def _change(row: md.Row, errors: list[str]) -> Change:
    c, n = row.cells, row.line
    day = md.parse_date(c["Date"], n, "Date", errors)
    amount = _amount(c["Amount"], n, "Amount", SIGNED_RE, "a signed number, not zero", errors)
    if amount == 0 and SIGNED_RE.fullmatch(c["Amount"]):
        errors.append(f"line {n}: Amount '{c['Amount']}' must not be zero")
    if not REFERENCE_RE.match(c["Change"]):
        errors.append(f"line {n}: Change '{c['Change']}' must be one change request or decision ID "
                      "(CR-NNN or D-NNN)")
    return Change(day, c["Line"], amount, c["Change"], n)


class _Scanner:
    """Line-by-line state machine: preamble -> Lines -> Rates -> Approved changes."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.title_seen = False
        self.currency: Optional[str] = None
        self.last_reviewed: Optional[date] = None
        self.last_reviewed_seen = False
        self.section = -1
        self.tables = (md.Table(LINE_COLUMNS), md.Table(RATE_COLUMNS), md.Table(CHANGE_COLUMNS))
        self.seen_tables = [False, False, False]

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
        elif line.startswith(CURRENCY) and self.section < 0 and self.currency is None:
            self._currency(number, line[len(CURRENCY):].strip())
        elif line.startswith(LAST_REVIEWED) and self.section < 0 and not self.last_reviewed_seen:
            self.last_reviewed_seen = True
            self.last_reviewed = md.parse_date(line[len(LAST_REVIEWED):].strip(), number, "Last reviewed",
                                               self.errors)
        elif line.startswith("## "):
            self._section(number, line)
        elif line.startswith("|") and self.section >= 0 and self.tables[self.section].open:
            self.seen_tables[self.section] = True
            self.tables[self.section].feed(number, line, self.errors)
        else:
            self.errors.append(f"line {number}: unexpected content: only the title, '{CURRENCY}', "
                               f"'{LAST_REVIEWED}', the sections and their tables are allowed")

    def _currency(self, number: int, value: str) -> None:
        self.currency = value
        if not CURRENCY_RE.match(value):
            self.errors.append(f"line {number}: Currency '{value}' must be an ISO 4217 code such as EUR")

    def _section(self, number: int, line: str) -> None:
        if line in SECTIONS and SECTIONS.index(line) == self.section + 1:
            self.section += 1
        else:
            self.errors.append(f"line {number}: unexpected section '{line}': the sections are "
                               f"{', '.join(SECTIONS)}, once each and in this order, the last one optional")


def _check_lines(lines: tuple[Line, ...], errors: list[str]) -> None:
    first: dict[int, int] = {}
    previous: Optional[Line] = None
    for item in lines:
        if not ID_RE.match(item.id):
            continue
        number = int(item.id[2:])
        if number in first:
            errors.append(f"line {item.line}: duplicate ID '{item.id}' (first on line {first[number]})")
        elif previous and number < int(previous.id[2:]):
            errors.append(f"line {item.line}: {item.id} comes after {previous.id}: keep lines in ID order")
        first.setdefault(number, item.line)
        previous = item


def _check_rates(rates: tuple[Rate, ...], errors: list[str]) -> None:
    seen: dict[tuple[str, date], int] = {}
    for rate in rates:
        if rate.start is None:
            continue
        key = (rate.role.casefold(), rate.start)
        if key in seen:
            errors.append(f"line {rate.line}: {rate.role} has another rate with the same From on line {seen[key]}")
        seen.setdefault(key, rate.line)


def _check_changes(register: Register, errors: list[str]) -> None:
    by_id = {item.id: item for item in register.lines}
    running = {item.id: item.amount for item in register.lines}
    for change in sorted(register.changes, key=lambda c: (c.day or date.min, c.line)):
        if change.target not in by_id:
            errors.append(f"line {change.line}: unknown line '{change.target}': use the ID of a budget line")
            continue
        running[change.target] += change.amount
        if running[change.target] < 0:
            errors.append(f"line {change.line}: this change takes {change.target} below zero "
                          f"({money(running[change.target])})")


def parse(text: str) -> tuple[Register, list[str]]:
    scanner = _Scanner()
    last = scanner.scan(text)
    errors = scanner.errors
    if not scanner.title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    if scanner.currency is None:
        errors.append(f"line 1: missing '{CURRENCY}' line (an ISO 4217 code such as EUR)")
    for index, heading in enumerate(SECTIONS):
        if scanner.section < index:
            if index < REQUIRED_SECTIONS:
                errors.append(f"line {last}: missing section '{heading}'")
        elif not scanner.seen_tables[index]:
            errors.append(f"line {last}: section '{heading}' has no table")
    lines = tuple(_line(row, errors) for row in scanner.tables[0].rows)
    rates = tuple(_rate(row, errors) for row in scanner.tables[1].rows)
    changes = tuple(_change(row, errors) for row in scanner.tables[2].rows)
    register = Register(scanner.currency or "", scanner.last_reviewed, lines, rates, changes)
    _check_lines(lines, errors)
    _check_rates(rates, errors)
    _check_changes(register, errors)
    return register, md.sort_errors(errors)


def validate(text: str) -> list[str]:
    return parse(text)[1]


@dataclass(frozen=True)
class LineTotal:
    line: Line
    changes: Decimal

    @property
    def current(self) -> Decimal:
        return self.line.amount + self.changes


@dataclass(frozen=True)
class Totals:
    lines: tuple[LineTotal, ...]

    def _sum(self, kinds: tuple[str, ...]) -> Decimal:
        return sum((t.current for t in self.lines if t.line.kind in kinds), Decimal(0))

    @property
    def bac(self) -> Decimal:
        return self._sum(BAC_KINDS)

    @property
    def contingency(self) -> Decimal:
        return self._sum((CONTINGENCY,))

    @property
    def management_reserve(self) -> Decimal:
        return self._sum((MANAGEMENT,))


def totals(register: Register, until: Optional[date] = None) -> Totals:
    """Each line with its approved changes (those dated up to `until`, when given)."""
    def counted(change: Change) -> bool:
        return until is None or (change.day is not None and change.day <= until)

    return Totals(tuple(LineTotal(item, sum((c.amount for c in register.changes
                                             if c.target == item.id and counted(c)), Decimal(0)))
                        for item in register.lines))


def rate_on(register: Register, role: str, day: date) -> Optional[Rate]:
    """The rate of a role in force on a day (role compared without case): the latest From on or before it."""
    rows = [r for r in register.rates if r.role.casefold() == role.strip().casefold() and r.start and r.start <= day]
    return max(rows, key=lambda r: r.start) if rows else None


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Budget register {name} is declared but missing: run {SKILL} to create it."
    register, errors = parse(text)
    if errors:
        return f"Budget register {name} has {len(errors)} validation errors: run {SKILL} to fix them."
    t = totals(register)
    reviewed = f"last reviewed {register.last_reviewed}" if register.last_reviewed else "never reviewed"
    cur = register.currency
    return (f"Budget register {name}: budget {money(t.bac)} {cur}, reserves "
            f"{money(t.contingency + t.management_reserve)} {cur} (contingency {money(t.contingency)}, "
            f"management reserve {money(t.management_reserve)}), {reviewed}.")


@dataclass(frozen=True)
class EarnedValue:
    bac: Decimal
    pv: Decimal
    ev: Decimal
    ac: Decimal
    cpi: Optional[Decimal]
    spi: Optional[Decimal]
    eac: Optional[Decimal]
    eac_cpi_spi: Optional[Decimal]
    tcpi: Optional[Decimal]

    @property
    def cv(self) -> Decimal:
        return self.ev - self.ac

    @property
    def sv(self) -> Decimal:
        return self.ev - self.pv

    @property
    def etc(self) -> Optional[Decimal]:
        return None if self.eac is None else self.eac - self.ac

    @property
    def vac(self) -> Optional[Decimal]:
        return None if self.eac is None else self.bac - self.eac


def _ratio(numerator: Decimal, denominator: Decimal) -> Optional[Decimal]:
    return None if denominator == 0 else numerator / denominator


def earned_value(bac: Decimal, pv: Decimal, ev: Decimal, ac: Decimal) -> EarnedValue:
    """The earned value figures; a figure that would divide by zero is None. Nothing is rounded here."""
    cpi, spi = _ratio(ev, ac), _ratio(ev, pv)
    eac = _ratio(bac * ac, ev) if cpi else None
    eac_cpi_spi = ac + (bac - ev) / (cpi * spi) if cpi and spi else None
    return EarnedValue(bac, pv, ev, ac, cpi, spi, eac, eac_cpi_spi, _ratio(bac - ev, bac - ac))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "evm":
        import budget_evm

        sys.exit(budget_evm.main(sys.argv[2:]))
    sys.exit(md.validate_cli(sys.argv[1:], "budget_register.py", validate))
