#!/usr/bin/env python3
"""The project manager's backlog: open actions plus what the other registers say is due, sorted by due date.

Read only. Each item names its origin ID (AC-, R-, S-, CR-, G-) and the register it comes from keeps it. Python 3
standard library only.

Usage:
    pm_backlog.py PROJECT.md [--owner NAME ...] [--days N] [--today YYYY-MM-DD]

    --owner  an owner as written in the registers (a team slug or a role), or "all"; repeat for several.
             Default: "Project manager". Change requests and gates have no owner: they belong to the project
             manager's view and to "all", and appear for no other owner.
    --days   keep dated items due within N days of today; overdue and undated items are always kept.

Exit status: 0 printed, 2 usage or I/O error.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Optional

import actions_register
import changes_register
import gates_register
import md_register as md
import project_register
import risks_register
import stakeholders_register

PM_ROLE = "Project manager"
ALL = ("all",)
COLUMNS = ("Due", "Days", "Origin", "Owner", "What")
UNOWNED_BY = "-"


@dataclass(frozen=True)
class Item:
    due: Optional[date]
    days: Optional[int]
    origin: str
    owner: str
    what: str


@dataclass(frozen=True)
class Backlog:
    items: tuple[Item, ...]
    notes: list[str]


class _Wanted:
    """Which owners the view is for."""

    def __init__(self, owners: tuple[str, ...]) -> None:
        self.names = {o.strip().lower() for o in owners}
        self.everyone = "all" in self.names

    def owns(self, owner: str) -> bool:
        return self.everyone or owner.strip().lower() in self.names

    @property
    def unowned(self) -> bool:
        """Change requests and gates belong to the project manager's view and to everyone's."""
        return self.everyone or PM_ROLE.lower() in self.names


def _item(due: Optional[date], origin: str, owner: str, what: str, today: date) -> Item:
    return Item(due, (due - today).days if due else None, origin, owner, what)


def _project_root(project_file: Path) -> Path:
    here = project_file.resolve()
    for folder in (here.parent, *here.parent.parents):
        found = project_register.find_project_register(folder)
        if found is not None and found.resolve() == here:
            return folder
    return here.parent


def _read(path: Path, label: str, name: str, notes: list[str]) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        notes.append(f"{label} ({name}) is declared but missing")
    except (OSError, UnicodeDecodeError) as exc:
        notes.append(f"{label} ({name}) cannot be read ({type(exc).__name__})")
    return None


def _parsed(path: Path, label: str, name: str, module, notes: list[str]):
    text = _read(path, label, name, notes)
    if text is None:
        return None
    parsed, errors = module.parse(text)
    if errors:
        notes.append(f"{label} ({name}) has {md.count_of(len(errors), 'validation error')}")
        return None
    return parsed


def _actions(parsed, wanted: _Wanted, today: date) -> list[Item]:
    items = []
    for a in parsed:
        if a.status == "open" and wanted.owns(a.owner):
            link = f" ({a.linked_item})" if a.linked_item else ""
            items.append(_item(a.due, a.id, a.owner, a.fields.get("Action", a.title) + link, today))
    return items


def _risks(register, wanted: _Wanted, today: date) -> list[Item]:
    return [_item(r.review, r.id, r.owner, f"Review {r.type}: {r.title}", today)
            for r in register.risks if r.status in risks_register.LIVE and wanted.owns(r.owner)]


def _stakeholders(register, wanted: _Wanted, today: date) -> list[Item]:
    return [_item(s.review, s.id, s.owner, f"Review stakeholder: {s.stakeholder}", today)
            for s in register.stakeholders if s.status == "active" and wanted.owns(s.owner)]


def _changes(parsed, wanted: _Wanted, today: date) -> list[Item]:
    if not wanted.unowned:
        return []
    what = {"proposed": "Assess change request", "approved": "Implement change"}
    return [_item(None, c.id, UNOWNED_BY, f"{what[c.status]}: {c.title}", today)
            for c in parsed if c.status in what]


def _gates(register, wanted: _Wanted, today: date) -> list[Item]:
    if not wanted.unowned:
        return []
    items = []
    last = {o.gate: o for o in register.outcomes}
    for g in register.gates:
        if g.status == "open" and g.planned:
            items.append(_item(g.planned, g.id, UNOWNED_BY, f"Gate review: {g.name}", today))
        outcome = last.get(g.id)
        if outcome and outcome.outcome == "go with conditions":
            items.append(_item(None, g.id, UNOWNED_BY,
                               f"Follow up the conditions of {g.name}: {outcome.conditions}", today))
    return items


SOURCES: tuple[tuple[str, str, object, Callable], ...] = (
    ("Action log", "actions", actions_register, _actions),
    ("Risk register", "risks", risks_register, _risks),
    ("Stakeholder register", "stakeholders", stakeholders_register, _stakeholders),
    ("Change log", "changes", changes_register, _changes),
    ("Gate register", "gates", gates_register, _gates),
)


def _sorted(items: list[Item]) -> tuple[Item, ...]:
    def key(i: Item):
        return (i.due is None, i.due or date.max, i.origin.split("-")[0], int(i.origin.split("-")[1]))
    return tuple(sorted(items, key=key))


def build(project_file: Path, owners: tuple[str, ...], today: date, horizon: Optional[int] = None) -> Backlog:
    """The backlog of the given owners, from the registers the project declares."""
    root = _project_root(project_file)
    declared = project_register.declared_registers(root, project_file)
    wanted, notes, items = _Wanted(owners), [], []
    for name, _, module, collect in SOURCES:
        path = declared.get(name)
        if path is None:
            continue
        label = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
        parsed = _parsed(path, label, name, module, notes)
        if parsed is not None:
            items += collect(parsed, wanted, today)
    if horizon is not None:
        items = [i for i in items if i.days is None or i.days <= horizon]
    return Backlog(_sorted(items), notes)


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render(backlog: Backlog) -> str:
    lines = []
    if backlog.items:
        lines += ["| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
        for i in backlog.items:
            cells = (str(i.due) if i.due else "-", str(i.days) if i.days is not None else "-", i.origin, i.owner,
                     i.what)
            lines.append("| " + " | ".join(_cell(c) for c in cells) + " |")
    else:
        lines.append("No open items.")
    if backlog.notes:
        lines += ["", "Not read: " + "; ".join(backlog.notes) + "."]
    return "\n".join(lines)


def _day(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a date (YYYY-MM-DD)")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="pm_backlog.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("project", type=Path, help="path to PROJECT.md")
    parser.add_argument("--owner", action="append", help="an owner, or 'all'; repeatable (default: Project manager)")
    parser.add_argument("--days", type=md.whole_number, help="horizon in days; overdue and undated items stay")
    parser.add_argument("--today", type=_day, default=None, help="the date to count from (default: today)")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    try:
        backlog = build(args.project, tuple(args.owner or (PM_ROLE,)), args.today or date.today(), args.days)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"cannot read {args.project}: {exc}", file=sys.stderr)
        return 2
    print(render(backlog))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
