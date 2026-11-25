#!/usr/bin/env python3
"""Three-point (PERT) estimates and the cost of effort at the rates of a budget register.

Python 3 standard library only. Numbers are Decimal; percentiles use the normal approximation.

Usage:
    estimate.py pert --optimistic O --likely M --pessimistic P [--unit LABEL]
    estimate.py pert --items CSV [--unit LABEL]       CSV header: item,optimistic,likely,pessimistic
    estimate.py cost --budget BUDGET.md --role ROLE --effort N --unit day|hour [--date YYYY-MM-DD]
                     [--hours-per-day H]
    exit 0 ok, 1 invalid data, 2 usage or I/O error
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
from statistics import NormalDist
from typing import Optional

import budget_register as br

ITEM_COLUMNS = ("item", "optimistic", "likely", "pessimistic")
NUMBER_RE = re.compile(r"[0-9]{1,%d}(\.[0-9]{1,%d})?" % (br.MAX_DIGITS, br.MAX_DIGITS))
PERCENTILES = (50, 85, 95)
RANGES = ((1, "68%"), (2, "95%"), (3, "99.7%"))
CENT = Decimal("0.01")
SIX = Decimal(6)


@dataclass(frozen=True)
class Item:
    name: str
    optimistic: Decimal
    likely: Decimal
    pessimistic: Decimal


@dataclass(frozen=True)
class Estimate:
    mean: Decimal
    variance: Decimal

    @property
    def sd(self) -> Decimal:
        return self.variance.sqrt()


def pert(optimistic: Decimal, likely: Decimal, pessimistic: Decimal) -> Estimate:
    """The PERT (beta) mean (O + 4M + P) / 6 and variance ((P - O) / 6)²."""
    return Estimate((optimistic + 4 * likely + pessimistic) / SIX, ((pessimistic - optimistic) / SIX) ** 2)


def total(items: list[Item]) -> Estimate:
    """The sum of independent estimates: means and variances add up."""
    estimates = [pert(i.optimistic, i.likely, i.pessimistic) for i in items]
    return Estimate(sum((e.mean for e in estimates), Decimal(0)), sum((e.variance for e in estimates), Decimal(0)))


def percentile(estimate: Estimate, percent: int) -> Decimal:
    """The value not exceeded with the given probability, by the normal approximation."""
    z = Decimal(repr(NormalDist().inv_cdf(percent / 100))) if percent != 50 else Decimal(0)
    return estimate.mean + z * estimate.sd


def fmt(value: Decimal) -> str:
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP, context=br.DISPLAY))


def plain(value: Decimal) -> str:
    """A number as typed, without trailing zeros, at most four decimals."""
    rounded = value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP, context=br.DISPLAY)
    return format(rounded.normalize(context=br.DISPLAY), "f")


class _Exit(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


def _number(value: str) -> Decimal:
    if not NUMBER_RE.fullmatch(value):
        raise argparse.ArgumentTypeError(f"'{value}' must be a number not below zero, at most {br.MAX_DIGITS} digits "
                                         "before and after the point, with a point as decimal mark")
    return Decimal(value)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise _Exit(2, f"cannot read {path}: {exc}")


def _order_error(o: Decimal, m: Decimal, p: Decimal) -> Optional[str]:
    return None if o <= m <= p else "optimistic <= likely <= pessimistic does not hold"


def parse_items(text: str) -> tuple[list[Item], list[str]]:
    reader = csv.reader(io.StringIO(text.lstrip("\ufeff")))
    errors: list[str] = []
    items: list[Item] = []
    seen: dict[str, int] = {}
    try:
        header = next(reader, None)
        if header is None or tuple(h.strip() for h in header) != ITEM_COLUMNS:
            return [], [f"line 1: the header must be exactly: {','.join(ITEM_COLUMNS)}"]
        for values in reader:
            n = reader.line_num
            if not any(v.strip() for v in values):
                continue
            item = _item([v.strip() for v in values], n, errors)
            if item is None:
                continue
            if item.name in seen:
                errors.append(f"line {n}: item '{item.name}' is already on line {seen[item.name]}")
            seen.setdefault(item.name, n)
            items.append(item)
    except csv.Error as exc:
        errors.append(f"line {max(reader.line_num, 1)}: {exc}")
    if not items and not errors:
        errors.append("line 1: there are no items")
    return items, errors


def _item(values: list[str], n: int, errors: list[str]) -> Optional[Item]:
    if len(values) != len(ITEM_COLUMNS):
        errors.append(f"line {n}: expected {len(ITEM_COLUMNS)} fields, found {len(values)}")
        return None
    if not values[0]:
        errors.append(f"line {n}: item is empty")
    numbers = []
    for name, value in zip(ITEM_COLUMNS[1:], values[1:]):
        if NUMBER_RE.fullmatch(value):
            numbers.append(Decimal(value))
        else:
            errors.append(f"line {n}: {name} '{value}' must be a number not below zero, at most {br.MAX_DIGITS} "
                          "digits before and after the point")
    if len(numbers) != 3:
        return None
    problem = _order_error(*numbers)
    if problem:
        errors.append(f"line {n}: {problem}")
    return Item(values[0], *numbers)


def _distribution(estimate: Estimate, unit: str) -> list[str]:
    lines = ["Ranges (normal approximation, floored at 0):"]
    for k, label in RANGES:
        low = max(Decimal(0), estimate.mean - k * estimate.sd)
        lines.append(f"  {label}: {fmt(low)} to {fmt(estimate.mean + k * estimate.sd)}{unit} (mean ± {k} sd)")
    lines.append("Not exceeded with probability (normal approximation):")
    lines += [f"  {p}%: {fmt(percentile(estimate, p))}{unit}" for p in PERCENTILES]
    return lines


def pert_report(o: Decimal, m: Decimal, p: Decimal, unit: str) -> str:
    e = pert(o, m, p)
    lines = [f"PERT (three-point, beta) estimate: O = {plain(o)}, M = {plain(m)}, P = {plain(p)}",
             f"Mean = (O + 4M + P) / 6 = ({plain(o)} + 4 × {plain(m)} + {plain(p)}) / 6 = {fmt(e.mean)}{unit}",
             f"Standard deviation = (P - O) / 6 = ({plain(p)} - {plain(o)}) / 6 = {fmt(e.sd)}{unit}"]
    return "\n".join(lines + _distribution(e, unit))


def items_report(items: list[Item], unit: str) -> str:
    lines = ["PERT per item: mean = (O + 4M + P) / 6, sd = (P - O) / 6, variance = sd²",
             "| Item | O | M | P | Mean | SD | Variance |", "|---|---|---|---|---|---|---|"]
    for i in items:
        e = pert(i.optimistic, i.likely, i.pessimistic)
        lines.append(f"| {i.name} | {plain(i.optimistic)} | {plain(i.likely)} | {plain(i.pessimistic)} | "
                     f"{fmt(e.mean)} | {fmt(e.sd)} | {fmt(e.variance)} |")
    t = total(items)
    lines += ["", f"Items: {len(items)}, assumed independent",
              f"Total mean: {fmt(t.mean)}{unit} (sum of the means)",
              f"Total standard deviation: {fmt(t.sd)}{unit} (square root of the sum of the variances, {fmt(t.variance)})"]
    return "\n".join(lines + _distribution(t, unit))


def _effort_in(effort: Decimal, unit: str, rate_unit: str, hours: Optional[Decimal]) -> tuple[Decimal, list[str]]:
    if unit == rate_unit:
        return effort, []
    if hours is None:
        raise _Exit(2, f"the rate is per {rate_unit} and the effort in {unit}s: give --hours-per-day")
    converted = effort * hours if unit == "day" else effort / hours
    op = "×" if unit == "day" else "/"
    return converted, [f"Effort = {plain(effort)} {unit} {op} {plain(hours)} hours per day = "
                       f"{plain(converted)} {rate_unit}"]


def cost_report(args: argparse.Namespace) -> str:
    register, errors = br.parse(_read(args.budget))
    if errors:
        raise _Exit(1, "\n".join([f"{args.budget} is not a valid budget register:"] + errors))
    day = args.date or date.today()
    rate = br.rate_on(register, args.role, day)
    if rate is None:
        roles = sorted({r.role for r in register.rates})
        raise _Exit(1, f"no rate for the role '{args.role}' on {day}; the roles with a rate are: "
                       f"{', '.join(roles) or 'none'}")
    effort, working = _effort_in(args.effort, args.unit, rate.unit, args.hours_per_day)
    cur = register.currency
    cost = effort * rate.rate
    lines = [f"Rate in force for {rate.role} on {day}: {br.money(rate.rate)} {cur} per {rate.unit} "
             f"(from {rate.start}, line {rate.line} of {args.budget.name})"] + working
    lines.append(f"Cost = {plain(effort)} {rate.unit} × {br.money(rate.rate)} {cur} = {fmt(cost)} {cur}")
    return "\n".join(lines)


def _pert_command(args: argparse.Namespace) -> str:
    unit = f" {args.unit}" if args.unit else ""
    three = (args.optimistic, args.likely, args.pessimistic)
    if args.items is not None:
        if any(v is not None for v in three):
            raise _Exit(2, "give either --items or --optimistic, --likely and --pessimistic")
        items, errors = parse_items(_read(args.items))
        if errors:
            raise _Exit(1, "\n".join([f"{args.items} is not valid:"] + errors))
        return items_report(items, unit)
    if any(v is None for v in three):
        raise _Exit(2, "give --optimistic, --likely and --pessimistic, or --items")
    problem = _order_error(*three)
    if problem:
        raise _Exit(1, problem)
    return pert_report(*three, unit)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="estimate.py")
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("pert")
    p.add_argument("--optimistic", type=_number)
    p.add_argument("--likely", type=_number)
    p.add_argument("--pessimistic", type=_number)
    p.add_argument("--items", type=Path)
    p.add_argument("--unit", default="")
    c = commands.add_parser("cost")
    c.add_argument("--budget", type=Path, required=True)
    c.add_argument("--role", required=True)
    c.add_argument("--effort", type=_number, required=True)
    c.add_argument("--unit", choices=br.UNITS, required=True)
    c.add_argument("--date", type=date.fromisoformat)
    c.add_argument("--hours-per-day", dest="hours_per_day", type=_number)
    return parser


def main(argv: list[str]) -> int:
    try:
        args = _parser().parse_args(argv)
    except SystemExit:
        return 2
    if args.command == "cost" and args.hours_per_day == 0:
        print("--hours-per-day must be above zero", file=sys.stderr)
        return 2
    try:
        print(_pert_command(args) if args.command == "pert" else cost_report(args))
    except _Exit as exc:
        print(exc, file=sys.stderr)
        return exc.code
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
