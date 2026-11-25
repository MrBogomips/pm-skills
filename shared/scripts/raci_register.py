#!/usr/bin/env python3
"""Parse and validate a RACI matrix (RACI.md).

The format is specified in shared/registers/raci.md. Python 3 standard library only.

Usage:
    raci_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# RACI"
FIXED = ("ID", "Deliverable", "WBS")
MIN_ROLES = 2
ID_RE = re.compile(r"^RA-[0-9]{3,}$")
WBS_RE = re.compile(r"^[0-9]+(\.[0-9]+)*$")
CELLS = ("", "R", "A", "C", "I", "A/R")
ACCOUNTABLE = ("A", "A/R")
RESPONSIBLE = ("R", "A/R")
SKILL = "/pm-skills:raci-matrix"


@dataclass(frozen=True)
class Assignment:
    id: str
    deliverable: str
    wbs: str
    cells: dict[str, str]
    line: int


@dataclass(frozen=True)
class Register:
    roles: tuple[str, ...]
    rows: tuple[Assignment, ...]


def _header(number: int, values: list[str], errors: list[str]) -> Optional[tuple[str, ...]]:
    """The roles of a valid header, or None when the fixed columns are wrong."""
    if tuple(values[:len(FIXED)]) != FIXED:
        errors.append(f"line {number}: columns must start with: {' | '.join(FIXED)}, then at least "
                      f"{MIN_ROLES} role columns")
        return None
    roles = tuple(values[len(FIXED):])
    if len(roles) < MIN_ROLES:
        errors.append(f"line {number}: the table needs at least two role columns after "
                      f"{' | '.join(FIXED)}")
    seen: set[str] = set()
    for role in roles:
        if not role:
            errors.append(f"line {number}: empty role column name")
        elif role in seen:
            errors.append(f"line {number}: duplicate role '{role}'")
        seen.add(role)
        md.check_contacts(number, "Role", role, errors)
    return roles


def _assignment(row: md.Row, roles: tuple[str, ...], errors: list[str]) -> Assignment:
    c, n = row.cells, row.line
    if not ID_RE.match(c["ID"]):
        errors.append(f"line {n}: ID '{c['ID']}' must be RA- followed by at least three digits (RA-001)")
    if not c["Deliverable"]:
        errors.append(f"line {n}: Deliverable is empty: name the deliverable or activity")
    if c["WBS"] and not WBS_RE.match(c["WBS"]):
        errors.append(f"line {n}: WBS '{c['WBS']}' must be empty or a dotted work package ID (1.2.3)")
    md.check_contacts(n, "Deliverable", c["Deliverable"], errors, phone=False)
    cells = {role: c[role] for role in roles}
    for role, value in cells.items():
        if value not in CELLS:
            errors.append(f"line {n}: {role} '{value}' must be one of: R, A, C, I, A/R, or empty")
    accountable = sum(1 for v in cells.values() if v in ACCOUNTABLE)
    if accountable != 1:
        found = "no A" if accountable == 0 else f"{accountable} A"
        errors.append(f"line {n}: {c['ID']} has {found}: exactly one A (or A/R) per row, one accountable role")
    if not any(v in RESPONSIBLE for v in cells.values()):
        errors.append(f"line {n}: {c['ID']} needs at least one R (or A/R): someone does the work")
    return Assignment(c["ID"], c["Deliverable"], c["WBS"], cells, n)


def parse(text: str) -> tuple[Register, list[str]]:
    errors: list[str] = []
    table: Optional[md.Table] = None
    roles: tuple[str, ...] = ()
    title_seen, table_seen, header_ok = False, False, False
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            if table is not None:
                table.close()
        elif line == TITLE and not title_seen and not table_seen:
            title_seen = True
        elif line.startswith("|") and title_seen and (table is None or table.open) and (header_ok or not table_seen):
            if not table_seen:
                table_seen = True
                values = md.cells(line)
                header = _header(number, values, errors)
                if header is None:
                    continue
                roles, header_ok = header, True
                table = md.Table(tuple(values))
            table.feed(number, line, errors)
        elif line.startswith("|") and table_seen and not header_ok:
            continue
        else:
            errors.append(f"line {number}: unexpected content: only the title '{TITLE}' and the RACI table "
                          "are allowed")
    if not title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    if not table_seen:
        errors.append(f"line 1: missing the RACI table ({' | '.join(FIXED)} | <roles>)")
    rows = tuple(_assignment(row, roles, errors) for row in (table.rows if table else []))
    first: dict[str, int] = {}
    for r in rows:
        if r.id in first:
            errors.append(f"line {r.line}: duplicate ID '{r.id}' (first on line {first[r.id]})")
        first.setdefault(r.id, r.line)
    return Register(roles, rows), md.sort_errors(errors)


def validate(text: str) -> list[str]:
    return parse(text)[1]


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"RACI matrix {name} is declared but missing: run {SKILL} to create it."
    register, errors = parse(text)
    if errors:
        return f"RACI matrix {name} has {md.count_of(len(errors), 'validation error')}: run {SKILL} to fix them."
    return (f"RACI matrix {name}: {md.count_of(len(register.rows), 'deliverable')}, "
            f"{md.count_of(len(register.roles), 'role')}.")


if __name__ == "__main__":
    sys.exit(md.validate_cli(sys.argv[1:], "raci_register.py", validate))
