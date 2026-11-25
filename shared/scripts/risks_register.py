#!/usr/bin/env python3
"""Parse and validate a risk register (RISKS.md).

The format is specified in shared/registers/risks.md. Python 3 standard library only.

Usage:
    risks_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# Risks"
COLUMNS = ("ID", "Type", "Risk", "Category", "Probability", "Impact", "Score", "Strategy", "Response", "Owner",
           "Status", "Raised", "Review")
SCALE_PREFIX = "Scale:"
LAST_REVIEWED = "Last reviewed:"
DEFAULT_SCALE = (1, 5)
SCALE_RE = re.compile(r"^([0-9]+)\s*-\s*([0-9]+)$")
ID_RE = re.compile(r"^R-[0-9]{3,}$")
TYPES = ("threat", "opportunity")
STRATEGIES = {
    "threat": ("avoid", "mitigate", "transfer", "accept", "escalate"),
    "opportunity": ("exploit", "enhance", "share", "accept", "escalate"),
}
STATUSES = ("open", "occurred", "closed")
LIVE = ("open", "occurred")
SKILL = "/pm-skills:risk-register"


@dataclass(frozen=True)
class Risk:
    id: str
    type: str
    title: str
    probability: Optional[int]
    impact: Optional[int]
    score: Optional[int]
    strategy: str
    owner: str
    status: str
    raised: Optional[date]
    review: Optional[date]
    line: int


@dataclass(frozen=True)
class Register:
    scale: tuple[int, int]
    last_reviewed: Optional[date]
    risks: tuple[Risk, ...]


def _int_in_scale(value: str, scale: tuple[int, int], what: str, line: int, errors: list[str]) -> Optional[int]:
    if not md.is_number(value) or not scale[0] <= int(value) <= scale[1]:
        errors.append(f"line {line}: {what} '{value}' must be a whole number from {scale[0]} to {scale[1]}")
        return None
    return int(value)


def _risk(row: md.Row, scale: tuple[int, int], errors: list[str]) -> Risk:
    c, n = row.cells, row.line
    if not ID_RE.match(c["ID"]):
        errors.append(f"line {n}: ID '{c['ID']}' must be R- followed by at least three digits (R-001)")
    if c["Type"] not in TYPES:
        errors.append(f"line {n}: Type '{c['Type']}' must be threat or opportunity")
    if not c["Risk"]:
        errors.append(f"line {n}: Risk is empty")
    probability = _int_in_scale(c["Probability"], scale, "Probability", n, errors)
    impact = _int_in_scale(c["Impact"], scale, "Impact", n, errors)
    score = int(c["Score"]) if md.is_number(c["Score"]) else None
    if probability is not None and impact is not None and score != probability * impact:
        errors.append(f"line {n}: Score '{c['Score']}' must be Probability × Impact = {probability * impact}")
    if c["Status"] not in STATUSES:
        errors.append(f"line {n}: Status '{c['Status']}' must be one of: {', '.join(STATUSES)}")
    allowed = STRATEGIES.get(c["Type"], ())
    if c["Strategy"] and allowed and c["Strategy"] not in allowed:
        errors.append(f"line {n}: Strategy '{c['Strategy']}' for a {c['Type']} must be one of: {', '.join(allowed)}")
    raised = md.parse_date(c["Raised"], n, "Raised", errors)
    review = md.parse_date(c["Review"], n, "Review", errors) if c["Review"] else None
    if c["Status"] in LIVE:
        for column in ("Strategy", "Owner", "Review"):
            if not c[column]:
                errors.append(f"line {n}: an {c['Status']} risk needs {column}")
    if raised and review and review < raised:
        errors.append(f"line {n}: Review {review} is before Raised {raised}")
    for column in ("Risk", "Category", "Response", "Owner"):
        md.check_contacts(n, column, c[column], errors)
    return Risk(c["ID"], c["Type"], c["Risk"], probability, impact, score, c["Strategy"], c["Owner"], c["Status"],
                raised, review, n)


def parse(text: str) -> tuple[Register, list[str]]:
    errors: list[str] = []
    table = md.Table(COLUMNS)
    title_seen, table_seen = False, False
    scale, last_reviewed = DEFAULT_SCALE, None
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            if table_seen:
                table.close()
            continue
        if line == TITLE and not title_seen and not table_seen:
            title_seen = True
        elif line.startswith(SCALE_PREFIX) and not table_seen:
            scale = _scale(line[len(SCALE_PREFIX):].strip(), number, errors)
        elif line.startswith(LAST_REVIEWED) and not table_seen:
            last_reviewed = md.parse_date(line[len(LAST_REVIEWED):].strip(), number, "Last reviewed", errors)
        elif line.startswith("|") and title_seen and table.open:
            table_seen = True
            table.feed(number, line, errors)
        else:
            errors.append(f"line {number}: unexpected content: only the title, '{SCALE_PREFIX}', "
                          f"'{LAST_REVIEWED}' and the risks table are allowed")
    if not title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    if not table_seen:
        errors.append(f"line 1: missing the risks table ({' | '.join(COLUMNS)})")
    risks = tuple(_risk(row, scale, errors) for row in table.rows)
    first: dict[str, int] = {}
    for risk in risks:
        if risk.id in first:
            errors.append(f"line {risk.line}: duplicate ID '{risk.id}' (first on line {first[risk.id]})")
        first.setdefault(risk.id, risk.line)
    return Register(scale, last_reviewed, risks), md.sort_errors(errors)


def _scale(value: str, number: int, errors: list[str]) -> tuple[int, int]:
    match = SCALE_RE.match(value)
    if not match or not 1 <= int(match.group(1)) < int(match.group(2)) <= 10:
        errors.append(f"line {number}: Scale '{value}' must be <low>-<high>, such as 1-5, with high at most 10")
        return DEFAULT_SCALE
    return int(match.group(1)), int(match.group(2))


def validate(text: str) -> list[str]:
    return parse(text)[1]


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Risk register {name} is declared but missing: run {SKILL} to create it."
    register, errors = parse(text)
    if errors:
        return f"Risk register {name} has {len(errors)} validation errors: run {SKILL} to fix them."
    live = [r for r in register.risks if r.status in LIVE]
    overdue = [r for r in live if r.review and r.review < today]
    occurred = sum(1 for r in live if r.status == "occurred")
    head = f"Risk register {name}: {len(live)} open" + (f" ({occurred} occurred)" if occurred else "")
    if overdue:
        return f"{head}, {len(overdue)} past their review date: run {SKILL} to review them."
    return f"{head}."


if __name__ == "__main__":
    sys.exit(md.validate_cli(sys.argv[1:], "risks_register.py", validate))
