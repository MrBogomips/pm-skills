#!/usr/bin/env python3
"""Parse and validate a tools register (TOOLS.md).

The format is specified in shared/registers/tools.md. Python 3 standard library only.

Usage:
    tools_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# Tools"
COLUMNS = ("Tool", "Purpose", "Access", "Scope", "Mode")
PURPOSES = ("issues", "code", "ci", "releases", "incidents", "schedule", "costs", "documents", "meetings",
            "messages", "calendar", "publish")
ACCESS_KINDS = ("mcp", "cli", "file", "skill", "script", "artifact")
ACCESS_RE = re.compile(r"^`?(" + "|".join(ACCESS_KINDS) + r"):(\S[^`]*)`?$")
MODES = ("read", "write")
SKILL = "/pm-skills:project-setup"


@dataclass(frozen=True)
class Tool:
    name: str
    purposes: tuple[str, ...]
    access_kind: str
    access_target: str
    scope: str
    mode: str
    line: int


def _tool(row: md.Row, errors: list[str]) -> Optional[Tool]:
    c, n = row.cells, row.line
    if not c["Tool"]:
        errors.append(f"line {n}: Tool is empty")
    purposes = md.split_list(c["Purpose"]) if c["Purpose"] else ()
    if not purposes:
        errors.append(f"line {n}: Purpose is empty; use one or more of: {', '.join(PURPOSES)}")
    for purpose in purposes:
        if purpose not in PURPOSES:
            errors.append(f"line {n}: Purpose '{purpose}' is not a capability; use: {', '.join(PURPOSES)}")
    access = ACCESS_RE.match(c["Access"])
    if not access:
        errors.append(f"line {n}: Access '{c['Access']}' must be <kind>:<target>, with kind one of: "
                      f"{', '.join(ACCESS_KINDS)}")
    if not c["Scope"]:
        errors.append(f"line {n}: Scope is empty: say what the tool covers")
    if c["Mode"] not in MODES:
        errors.append(f"line {n}: Mode '{c['Mode']}' must be read or write")
    for column in ("Tool", "Scope"):
        md.check_contacts(n, column, c[column], errors, phone=False)
    if not access:
        return None
    return Tool(c["Tool"], purposes, access.group(1), access.group(2).strip(), c["Scope"], c["Mode"], n)


def parse(text: str) -> tuple[tuple[Tool, ...], list[str]]:
    errors: list[str] = []
    table = md.Table(COLUMNS)
    title_seen, table_seen = False, False
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            if table_seen:
                table.close()
            continue
        if line == TITLE and not title_seen and not table_seen:
            title_seen = True
        elif line.startswith("|") and title_seen and table.open:
            table_seen = True
            table.feed(number, line, errors)
        else:
            errors.append(f"line {number}: unexpected content: only the title '{TITLE}' and the tools table "
                          "are allowed")
    if not title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    if not table_seen:
        errors.append(f"line 1: missing the tools table ({' | '.join(COLUMNS)})")
    tools = tuple(t for t in (_tool(row, errors) for row in table.rows) if t is not None)
    keys = Counter((t.name, t.access_kind, t.access_target, t.scope) for t in tools)
    for tool in tools:
        if keys[(tool.name, tool.access_kind, tool.access_target, tool.scope)] > 1:
            errors.append(f"line {tool.line}: duplicate row for {tool.name} with the same access and scope")
    return tools, md.sort_errors(errors)


def validate(text: str) -> list[str]:
    return parse(text)[1]


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Tools register {name} is declared but missing: run {SKILL} to create it."
    tools, errors = parse(text)
    if errors:
        return f"Tools register {name} has {len(errors)} validation errors: run {SKILL} to fix them."
    writable = sum(1 for t in tools if t.mode == "write")
    return f"Tools register {name}: {len(tools)} tools, {writable} with write access."


if __name__ == "__main__":
    sys.exit(md.validate_cli(sys.argv[1:], "tools_register.py", validate))
