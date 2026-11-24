#!/usr/bin/env python3
"""Find, parse and validate a project register (PROJECT.md).

The format is specified in shared/registers/project.md. Python 3 standard library only.

Usage:
    project_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable, Optional

import md_register as md

TITLE = "# Project"
SECTIONS = ("Identity", "Profile", "Conventions", "Registers")
INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md")
DECLARATION_RE = re.compile(r"^\s*-\s*Project register:\s*`([^`]+)`")
LEGACY_TEAM_RE = re.compile(r"^\s*-\s*Team register:\s*`([^`]+)`")
SKILL = "/pm-skills:project-setup"

CONTRACT_TYPES = ("fixed price", "time and materials", "internal")
DELIVERY_APPROACHES = ("predictive", "agile", "hybrid")
NAMING_PRESETS = ("by date", "coded")
YES_NO = ("yes", "no")
CODE_RE = re.compile(r"^[A-Z][A-Z0-9]{1,9}$")
TYPE_CODE_RE = re.compile(r"^([a-z0-9]+(?:-[a-z0-9]+)*)=([A-Z][A-Z0-9]{0,5})$")

# Register name in the Registers section -> its format file in shared/registers/.
REGISTERS = {
    "Tools register": "tools.md",
    "Team register": "teams.md",
    "Tailoring register": "tailoring.md",
    "Risk register": "risks.md",
    "Decision log": "decisions.md",
}


def _any(value: str) -> Optional[str]:
    return None


def _one_of(options: tuple[str, ...]) -> Callable[[str], Optional[str]]:
    def check(value: str) -> Optional[str]:
        return None if value in options else f"must be one of: {', '.join(options)}"
    return check


def _date(value: str) -> Optional[str]:
    errors: list[str] = []
    md.parse_date(value, 0, "date", errors)
    return "must be a date (YYYY-MM-DD)" if errors else None


def _code(value: str) -> Optional[str]:
    return None if CODE_RE.match(value) else "must be 2 to 10 capital letters or digits, starting with a letter"


def _weeks(value: str) -> Optional[str]:
    return None if md.is_number(value) and 1 <= int(value) <= 8 else "must be a number of weeks from 1 to 8"


def _path(value: str) -> Optional[str]:
    return None if md.backtick_path(value) else "must be a path between backticks"


def _type_codes(value: str) -> Optional[str]:
    items = md.split_list(value)
    bad = [i for i in items if not TYPE_CODE_RE.match(i)]
    if bad:
        return f"items must be <document type>=<CODE> (for example status-report=SAL), not: {', '.join(bad)}"
    types = [TYPE_CODE_RE.match(i).group(1) for i in items]
    return "a document type appears twice" if len(set(types)) != len(types) else None


KEYS: dict[str, dict[str, Callable[[str], Optional[str]]]] = {
    "Identity": {
        "Client": _any, "Project name": _any, "Internal code": _code, "Client code": _any,
        "Start date": _date, "Planned end date": _date, "Contract type": _one_of(CONTRACT_TYPES),
        "Deliverable language": _any,
    },
    "Profile": {
        "Delivery approach": _one_of(DELIVERY_APPROACHES), "Reporting cadence": _any, "Agile framework": _any,
        "Sprint length": _weeks, "Definition of Done": _path, "Definition of Workflow": _path,
    },
    "Conventions": {
        "Naming": _one_of(NAMING_PRESETS), "Type codes": _type_codes, "Version in file name": _one_of(YES_NO),
    },
    "Registers": {name: _path for name in REGISTERS},
}


@dataclass(frozen=True)
class Project:
    values: dict[str, dict[str, str]] = field(default_factory=dict)
    lines: dict[tuple[str, str], int] = field(default_factory=dict)

    def get(self, section: str, key: str) -> Optional[str]:
        return self.values.get(section, {}).get(key)

    def registers(self) -> dict[str, str]:
        """Register name -> path relative to the project root, as declared."""
        return {name: md.backtick_path(value) or "" for name, value in self.values.get("Registers", {}).items()}

    def type_codes(self) -> dict[str, str]:
        value = self.get("Conventions", "Type codes")
        if not value:
            return {}
        pairs = (TYPE_CODE_RE.match(item) for item in md.split_list(value))
        return {m.group(1): m.group(2) for m in pairs if m}


def parse(text: str) -> tuple[Project, list[str]]:
    errors: list[str] = []
    values: dict[str, dict[str, str]] = {s: {} for s in SECTIONS}
    lines: dict[tuple[str, str], int] = {}
    title_seen, section, order = False, None, 0
    seen_sections: set[str] = set()
    last = 0
    for number, raw in enumerate(text.splitlines(), start=1):
        last, line = number, raw.strip()
        if not line:
            continue
        if line == TITLE and not title_seen and section is None:
            title_seen = True
            continue
        if line.startswith("## "):
            name = line[3:].strip()
            if name in SECTIONS and SECTIONS.index(name) >= order:
                section, order = name, SECTIONS.index(name) + 1
                seen_sections.add(name)
            else:
                errors.append(f"line {number}: unexpected section '{name}': the sections are "
                              f"{', '.join(SECTIONS)}, once each and in this order")
            continue
        parsed = md.entry(line) if section else None
        if parsed is None:
            errors.append(f"line {number}: unexpected content: only the title, the four sections and "
                          "'- Key: value' entries are allowed")
            continue
        key, value = parsed
        _entry(section, key, value, number, values, lines, errors)
    if not title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    for name in SECTIONS:
        if name not in seen_sections:
            errors.append(f"line {last}: missing section '## {name}'")
    project = Project(values, lines)
    _cross_checks(project, errors)
    return project, md.sort_errors(errors)


def _entry(section: str, key: str, value: str, number: int, values: dict[str, dict[str, str]],
           lines: dict[tuple[str, str], int], errors: list[str]) -> None:
    allowed = KEYS[section]
    if key not in allowed:
        errors.append(f"line {number}: unknown key '{key}' in {section}; the keys are: {', '.join(allowed)}")
        return
    if (section, key) in lines:
        errors.append(f"line {number}: '{key}' is already on line {lines[(section, key)]}")
        return
    if not value:
        errors.append(f"line {number}: '{key}' is empty: leave the line out until the value is known")
        return
    problem = allowed[key](value)
    if problem:
        errors.append(f"line {number}: {key} '{value}' {problem}")
    md.check_contacts(number, key, value, errors, phone=key not in ("Client code", "Internal code"))
    values[section][key] = value
    lines[(section, key)] = number


def _cross_checks(project: Project, errors: list[str]) -> None:
    start, end = project.get("Identity", "Start date"), project.get("Identity", "Planned end date")
    if start and end and md.DATE_RE.match(start) and md.DATE_RE.match(end) and start > end:
        errors.append(f"line {project.lines[('Identity', 'Planned end date')]}: Planned end date {end} "
                      f"is before Start date {start}")
    if project.get("Conventions", "Naming") == "coded" and not project.get("Identity", "Internal code"):
        errors.append(f"line {project.lines[('Conventions', 'Naming')]}: the coded naming preset needs "
                      "Internal code in Identity")
    seen: dict[str, str] = {}
    for name, raw in project.registers().items():
        path = os.path.normpath(raw) if raw else raw
        if path in seen:
            errors.append(f"line {project.lines[('Registers', name)]}: {name} uses the same file as {seen[path]}")
        seen.setdefault(path, name)


def validate(text: str) -> list[str]:
    return parse(text)[1]


def _declared(project_dir: Path, pattern: re.Pattern) -> Optional[Path]:
    for name in INSTRUCTION_FILES:
        try:
            lines = (project_dir / name).read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        in_fence = False
        for line in lines:
            if md.FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            match = None if in_fence else pattern.match(line)
            if match:
                return project_dir / match.group(1)
    return None


def find_project_register(project_dir: Path) -> Optional[Path]:
    """The register declared by a "- Project register: `<path>`" line in AGENTS.md, else CLAUDE.md."""
    return _declared(project_dir, DECLARATION_RE)


def find_legacy_team_register(project_dir: Path) -> Optional[Path]:
    """A team register still declared in AGENTS.md or CLAUDE.md, as before pm-skills 1.0."""
    return _declared(project_dir, LEGACY_TEAM_RE)


def declared_registers(project_dir: Path, project_file: Path) -> dict[str, Path]:
    """Register name -> absolute path, from the Registers section of a readable PROJECT.md."""
    project, _ = parse(project_file.read_text(encoding="utf-8"))
    return {name: project_dir / path for name, path in project.registers().items() if path}


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Project register {name} is declared but missing: run {SKILL} to create it."
    project, errors = parse(text)
    if errors:
        return f"Project register {name} has {len(errors)} validation errors: run {SKILL} to fix them."
    title = project.get("Identity", "Project name") or "unnamed project"
    code = project.get("Identity", "Internal code")
    approach = project.get("Profile", "Delivery approach")
    details = f"{title}" + (f" ({code})" if code else "") + (f", {approach}" if approach else "")
    return f"Project register {name}: {details}."


if __name__ == "__main__":
    sys.exit(md.validate_cli(sys.argv[1:], "project_register.py", validate))
