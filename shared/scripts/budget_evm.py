"""The `evm` command of budget_register.py: earned value figures at a status date, with the working.

See shared/registers/budget.md. Python 3 standard library only.
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Optional

import budget_register as br
import md_register as md

DATA_COLUMNS = ("date", "pv", "ev", "ac")
NUMBER_RE = re.compile(r"[0-9]{1,%d}(\.[0-9]{1,2})?" % br.MAX_DIGITS)
CENT = Decimal("0.01")


@dataclass(frozen=True)
class Period:
    day: date
    pv: Decimal
    ev: Decimal
    ac: Decimal


class _Exit(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


def fmt(value: Optional[Decimal]) -> str:
    return "n/a" if value is None else str(value.quantize(CENT, rounding=ROUND_HALF_UP, context=br.DISPLAY))


def _number(value: str) -> Decimal:
    if not NUMBER_RE.fullmatch(value):
        raise argparse.ArgumentTypeError(f"'{value}' must be a number not below zero, at most {br.MAX_DIGITS} digits "
                                         "before the point and two after it, with a point as decimal mark")
    return Decimal(value)


def parse_data(text: str) -> tuple[tuple[Period, ...], list[str]]:
    """Cumulative PV, EV and AC per period, as CSV with the header date,pv,ev,ac, dates in increasing order."""
    reader = csv.reader(io.StringIO(text.lstrip("\ufeff")))
    errors: list[str] = []
    periods: list[Period] = []
    try:
        header = next(reader, None)
        if header is None or tuple(h.strip() for h in header) != DATA_COLUMNS:
            return (), [f"line 1: the header must be exactly: {','.join(DATA_COLUMNS)}"]
        for values in reader:
            n = reader.line_num
            if not any(v.strip() for v in values):
                continue
            period = _period([v.strip() for v in values], n, errors)
            if period is None:
                continue
            if periods and period.day <= periods[-1].day:
                errors.append(f"line {n}: date {period.day} is not after {periods[-1].day}: one row per period, "
                              "in order")
            periods.append(period)
    except csv.Error as exc:
        errors.append(f"line {max(reader.line_num, 1)}: {exc}")
    return tuple(periods), errors


def _period(values: list[str], n: int, errors: list[str]) -> Optional[Period]:
    if len(values) != len(DATA_COLUMNS):
        errors.append(f"line {n}: expected {len(DATA_COLUMNS)} fields, found {len(values)}")
        return None
    day = md.parse_date(values[0], n, "date", errors)
    amounts = []
    for name, value in zip(DATA_COLUMNS[1:], values[1:]):
        if NUMBER_RE.fullmatch(value):
            amounts.append(Decimal(value))
        else:
            errors.append(f"line {n}: {name} '{value}' must be a number not below zero, at most {br.MAX_DIGITS} "
                          "digits before the point and two after it")
    return Period(day, *amounts) if day and len(amounts) == 3 else None


def _lines_working(totals: br.Totals, currency: str) -> list[str]:
    lines = []
    for t in totals.lines:
        if t.line.kind not in br.BAC_KINDS:
            continue
        change = f" {'+' if t.changes >= 0 else '-'} {br.money(abs(t.changes))}" if t.changes else ""
        lines.append(f"  {t.line.id} {t.line.name} ({t.line.kind}): {br.money(t.line.amount)}{change} = "
                     f"{br.money(t.current)}")
    lines.append(f"BAC = {br.money(totals.bac)} {currency}")
    return lines


def _figures(r: br.EarnedValue, cpi_spi: bool) -> list[str]:
    bac, pv, ev, ac = fmt(r.bac), fmt(r.pv), fmt(r.ev), fmt(r.ac)
    lines = [f"CV = EV - AC = {ev} - {ac} = {fmt(r.cv)}",
             f"SV = EV - PV = {ev} - {pv} = {fmt(r.sv)}",
             f"CPI = EV / AC = {ev} / {ac} = {fmt(r.cpi)}",
             f"SPI = EV / PV = {ev} / {pv} = {fmt(r.spi)}",
             f"EAC = BAC / CPI = BAC × AC / EV = {bac} × {ac} / {ev} = {fmt(r.eac)}"]
    if cpi_spi:
        lines.append(f"EAC (CPI × SPI) = AC + (BAC - EV) / (CPI × SPI) = {ac} + {fmt(r.bac - r.ev)} / "
                     f"({fmt(r.cpi)} × {fmt(r.spi)}) = {fmt(r.eac_cpi_spi)}  (indices unrounded in the computation)")
    lines += [f"ETC = EAC - AC = {fmt(r.eac)} - {ac} = {fmt(r.etc)}",
              f"VAC = BAC - EAC = {bac} - {fmt(r.eac)} = {fmt(r.vac)}",
              f"TCPI = (BAC - EV) / (BAC - AC) = {fmt(r.bac - r.ev)} / {fmt(r.bac - r.ac)} = {fmt(r.tcpi)}"]
    return lines


def _warnings(r: br.EarnedValue) -> list[str]:
    notes = []
    if r.ev > r.bac:
        notes.append("Note: EV is above BAC: check the earned value or the approved changes.")
    if r.pv > r.bac:
        notes.append("Note: PV is above BAC: check the planned value or the approved changes.")
    return notes


def _trend(periods: tuple[Period, ...]) -> list[str]:
    lines = ["Trend (cumulative):", "| Date | PV | EV | AC | CPI | SPI |", "|---|---|---|---|---|---|"]
    for p in periods:
        r = br.earned_value(Decimal(0), p.pv, p.ev, p.ac)
        lines.append(f"| {p.day} | {fmt(p.pv)} | {fmt(p.ev)} | {fmt(p.ac)} | {fmt(r.cpi)} | {fmt(r.spi)} |")
    return lines


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise _Exit(2, f"cannot read {path}: {exc}")


def _values(args: argparse.Namespace) -> tuple[Period, list[str], str]:
    if args.data is None:
        return Period(args.status_date, args.pv, args.ev, args.ac), [], "the command line"
    periods, errors = parse_data(_read(args.data))
    if errors:
        raise _Exit(1, "\n".join([f"{args.data} is not valid:"] + errors))
    used = tuple(p for p in periods if p.day <= args.status_date)
    if not used:
        raise _Exit(1, f"{args.data} has no row on or before the status date {args.status_date}")
    return used[-1], _trend(used), f"{args.data}, row of {used[-1].day}"


def run(args: argparse.Namespace) -> str:
    register, errors = br.parse(_read(args.file))
    if errors:
        raise _Exit(1, "\n".join([f"{args.file} is not a valid budget register:"] + errors))
    period, trend, source = _values(args)
    totals = br.totals(register, until=args.status_date)
    result = br.earned_value(totals.bac, period.pv, period.ev, period.ac)
    cur = register.currency
    lines = [f"Status date: {args.status_date}",
             f"BAC: the labor and expense lines with the approved changes dated up to {args.status_date}"]
    lines += _lines_working(totals, cur)
    lines.append(f"Reserves, not in BAC: contingency {br.money(totals.contingency)}, management reserve "
                 f"{br.money(totals.management_reserve)} {cur}")
    lines += ["", f"PV = {fmt(period.pv)}, EV = {fmt(period.ev)}, AC = {fmt(period.ac)} {cur} (from {source})"]
    lines += _figures(result, args.eac_cpi_spi) + _warnings(result)
    lines.append("Amounts in " + cur + ", two decimals; indices rounded to two decimals for display only.")
    if trend:
        lines += [""] + trend
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="budget_register.py evm")
    parser.add_argument("file", type=Path)
    parser.add_argument("--status-date", dest="status_date", required=True, type=date.fromisoformat)
    parser.add_argument("--pv", type=_number)
    parser.add_argument("--ev", type=_number)
    parser.add_argument("--ac", type=_number)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--eac-cpi-spi", dest="eac_cpi_spi", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2
    given = [v is not None for v in (args.pv, args.ev, args.ac)]
    if (args.data is None) != all(given) or (args.data is not None and any(given)):
        print("give either --pv, --ev and --ac, or --data", file=sys.stderr)
        return 2
    try:
        print(run(args))
    except _Exit as exc:
        print(exc, file=sys.stderr)
        return exc.code
    return 0
