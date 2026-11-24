#!/usr/bin/env python3
"""Parse and validate a tailoring register (TAILORING.md) against the extension points the plugin's skills declare.

The format is specified in shared/registers/tailoring.md; extension points are declared in the
"## Extension points" section of each skill's SKILL.md. Python 3 standard library only.

Usage:
    tailoring_register.py validate FILE    exit 0 valid, 1 invalid (errors on stdout), 2 usage or I/O error
    tailoring_register.py points           the extension points declared by each skill
"""
from __future__ import annotations

import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import md_register as md

TITLE = "# Tailoring"
POINTS = ("format", "scale", "rules", "steps", "terms")
POINTS_HEADING = "## Extension points"
POINT_LINE_RE = re.compile(r"^-\s+`([a-z]+)`\s*:")
SKILL = "/pm-skills:pm-tailoring"
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parent.parent.parent)


def declared_points(plugin_root: Path = PLUGIN_ROOT) -> dict[str, tuple[str, ...]]:
    """Skill name -> extension points listed in its SKILL.md (an empty tuple when it declares none)."""
    result: dict[str, tuple[str, ...]] = {}
    for skill_file in sorted((plugin_root / "skills").glob("*/SKILL.md")):
        points: list[str] = []
        in_section = False
        for raw in skill_file.read_text(encoding="utf-8").splitlines():
            if raw.startswith("## "):
                in_section = raw.strip() == POINTS_HEADING
                continue
            match = POINT_LINE_RE.match(raw.strip()) if in_section else None
            if match:
                points.append(match.group(1))
        result[skill_file.parent.name] = tuple(points)
    return result


def parse(text: str, points: Optional[dict[str, tuple[str, ...]]] = None) -> tuple[dict[str, dict[str, int]], list[str]]:
    """Skill -> point -> number of rule lines; and the errors."""
    points = declared_points() if points is None else points
    errors: list[str] = []
    rules: dict[str, dict[str, int]] = {}
    title_seen, skill, point = False, None, None
    skipping = False  # inside a section or point already reported as invalid
    headings: dict[tuple[str, Optional[str]], int] = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if line == TITLE and not title_seen and skill is None and not skipping:
            title_seen = True
        elif line.startswith("## "):
            skill, point = _skill(line[3:].strip(), number, points, headings, errors), None
            skipping = skill is None
            if skill:
                rules.setdefault(skill, {})
        elif line.startswith("### "):
            if skill is None and not skipping:
                errors.append(f"line {number}: an extension point comes under a '## <skill>' section")
            point = _point(line[4:].strip(), skill, number, points, headings, errors) if skill else None
            skipping = point is None
            if point:
                rules[skill].setdefault(point, 0)
        elif skill and point:
            md.check_contacts(number, f"{skill} {point}", line, errors)
            rules[skill][point] += 1
        elif not skipping:
            errors.append(f"line {number}: unexpected content: only the title, '## <skill>' sections and "
                          "'### <extension point>' headings with their rules are allowed")
    if not title_seen:
        errors.append(f"line 1: missing title '{TITLE}'")
    for skill_name, by_point in rules.items():
        for point_name, count in by_point.items():
            if count == 0:
                errors.append(f"line {headings[(skill_name, point_name)]}: {skill_name} {point_name} has no rule")
    return rules, md.sort_errors(errors)


def _skill(name: str, number: int, points: dict[str, tuple[str, ...]],
           headings: dict[tuple[str, Optional[str]], int], errors: list[str]) -> Optional[str]:
    if name not in points:
        errors.append(f"line {number}: '{name}' is not a skill of the plugin")
        return None
    if not points[name]:
        errors.append(f"line {number}: {name} declares no extension points")
        return None
    if (name, None) in headings:
        errors.append(f"line {number}: section '{name}' is already on line {headings[(name, None)]}")
        return None
    headings[(name, None)] = number
    return name


def _point(name: str, skill: str, number: int, points: dict[str, tuple[str, ...]],
           headings: dict[tuple[str, Optional[str]], int], errors: list[str]) -> Optional[str]:
    if name not in POINTS:
        errors.append(f"line {number}: '{name}' is not an extension point; use one of: {', '.join(POINTS)}")
        return None
    if name not in points[skill]:
        errors.append(f"line {number}: {skill} does not declare the extension point '{name}' "
                      f"(it declares: {', '.join(points[skill])})")
        return None
    if (skill, name) in headings:
        errors.append(f"line {number}: {skill} {name} is already on line {headings[(skill, name)]}")
        return None
    headings[(skill, name)] = number
    return name


def validate(text: str) -> list[str]:
    return parse(text)[1]


def summary_line(path: Path, today: date, label: Optional[str] = None) -> str:
    name = f"`{label or path.name}`"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Tailoring register {name} is declared but missing."
    rules, errors = parse(text)
    if errors:
        return f"Tailoring register {name} has {len(errors)} validation errors: fix them before relying on it."
    tailored = sorted(rules)
    if not tailored:
        return f"Tailoring register {name}: no skill tailored."
    return f"Tailoring register {name}: rules for {', '.join(tailored)}."


def _cli(argv: list[str]) -> int:
    if argv == ["points"]:
        for skill_name, skill_points in declared_points().items():
            print(f"{skill_name}: {', '.join(skill_points) if skill_points else 'none'}")
        return 0
    return md.validate_cli(argv, "tailoring_register.py", validate)


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
