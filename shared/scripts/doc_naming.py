#!/usr/bin/env python3
"""File names and versions of project documents, from the Conventions of the project register.

The rules are in shared/documents/common.md. Python 3 standard library only.

Usage:
    doc_naming.py next --project PROJECT.md --dir DIR --type TYPE [--date YYYY-MM-DD] [--slug SLUG] [--version X.Y.Z]
        prints the path, relative to DIR, of a new document of TYPE; exit 3 when that name is already taken
    doc_naming.py bump VERSION major|minor|patch
        prints the next version
Exit 2 on a usage error or an unreadable or invalid project register.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import project_register

DEFAULT_CODES = {
    "status-report": "SR",
    "meeting-minutes": "MM",
    "meeting-brief": "MB",
    "project-charter": "PC",
    "lessons-learned": "LL",
    "sprint-planning": "SP",
    "sprint-review": "SV",
    "retrospective": "RT",
    "product-roadmap": "RM",
    "release-plan": "RP",
    "wbs": "WBS",
    "communication-plan": "CP",
    "team-charter": "TC",
    "phase-gate-review": "GR",
}
TYPE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)$")


class NamingError(ValueError):
    pass


def type_code(doc_type: str, overrides: dict[str, str]) -> str:
    code = overrides.get(doc_type) or DEFAULT_CODES.get(doc_type)
    if not code:
        raise NamingError(f"no type code for '{doc_type}': add it to Type codes in the Conventions of PROJECT.md")
    return code


def _slugify(slug: Optional[str]) -> str:
    if not slug:
        return ""
    clean = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
    return f"-{clean}" if clean else ""


def _with_version(stem: str, version: Optional[str], on: bool) -> str:
    if not on:
        return stem
    if not version or not SEMVER_RE.match(version):
        raise NamingError("the version in the file name is on: give --version as X.Y.Z")
    return f"{stem}-{version}"


def _free(base: Path, relative: str, versioned: bool) -> str:
    """The name itself, or with a +N suffix when the version is in the name and the name is taken."""
    if not (base / relative).exists():
        return relative
    if not versioned:
        raise FileExistsError(relative)
    stem = relative[:-3]
    n = 1
    while (base / f"{stem}+{n}.md").exists():
        n += 1
    return f"{stem}+{n}.md"


def next_name(project: project_register.Project, base: Path, doc_type: str, when: date,
              slug: Optional[str] = None, version: Optional[str] = None) -> str:
    if not TYPE_RE.match(doc_type):
        raise NamingError(f"document type '{doc_type}' must be lowercase words joined by hyphens")
    preset = project.get("Conventions", "Naming") or "by date"
    versioned = project.get("Conventions", "Version in file name") == "yes"
    suffix = _slugify(slug)
    if preset == "by date":
        stem = _with_version(f"{doc_type}/{when.isoformat()}-{doc_type}{suffix}", version, versioned)
        return _free(base, f"{stem}.md", versioned)
    proj = project.get("Identity", "Internal code")
    if not proj:
        raise NamingError("the coded preset needs Internal code in the Identity of PROJECT.md")
    code = type_code(doc_type, project.type_codes())
    prefix = f"{proj}-{code}-"
    pattern = re.compile(re.escape(prefix) + r"([0-9]{3,})")
    numbers = [int(m.group(1)) for p in base.glob(f"{prefix}*.md") if (m := pattern.match(p.name))]
    stem = _with_version(f"{prefix}{max(numbers, default=0) + 1:03d}{suffix}", version, versioned)
    return _free(base, f"{stem}.md", versioned)


def bump(version: str, part: str) -> str:
    match = SEMVER_RE.match(version)
    if not match or part not in ("major", "minor", "patch"):
        raise NamingError("usage: bump X.Y.Z major|minor|patch")
    major, minor, patch = (int(g) for g in match.groups())
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def _cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="doc_naming.py")
    sub = parser.add_subparsers(dest="command", required=True)
    nxt = sub.add_parser("next")
    nxt.add_argument("--project", required=True)
    nxt.add_argument("--dir", required=True)
    nxt.add_argument("--type", required=True)
    nxt.add_argument("--date", default=date.today().isoformat())
    nxt.add_argument("--slug")
    nxt.add_argument("--version")
    bmp = sub.add_parser("bump")
    bmp.add_argument("version")
    bmp.add_argument("part")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2
    try:
        if args.command == "bump":
            print(bump(args.version, args.part))
            return 0
        project, errors = project_register.parse(Path(args.project).read_text(encoding="utf-8"))
        if errors:
            print(f"{args.project} is not valid: run project_register.py validate", file=sys.stderr)
            return 2
        print(next_name(project, Path(args.dir), args.type, date.fromisoformat(args.date), args.slug, args.version))
        return 0
    except FileExistsError as exc:
        print(f"{exc} already exists: give a slug, or revise the existing document", file=sys.stderr)
        return 3
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
