"""The registers a project can declare, with the module that validates and sums up each one.

Used by the hooks: the project register (PROJECT.md) is declared in the project's AGENTS.md or CLAUDE.md, and every
other register in the Registers section of PROJECT.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import ModuleType
from typing import Optional

import budget_register
import capacity_register
import changes_register
import decisions_register
import gates_register
import project_register
import raci_register
import risks_register
import schedule_register
import stakeholders_register
import tailoring_register
import teams_register
import tools_register

PROJECT = "Project register"
MODULES: dict[str, ModuleType] = {
    PROJECT: project_register,
    "Tools register": tools_register,
    "Team register": teams_register,
    "Tailoring register": tailoring_register,
    "Risk register": risks_register,
    "Decision log": decisions_register,
    "Stakeholder register": stakeholders_register,
    "Capacity register": capacity_register,
    "Change log": changes_register,
    "Budget register": budget_register,
    "Schedule register": schedule_register,
    "RACI matrix": raci_register,
    "Gate register": gates_register,
}


@dataclass(frozen=True)
class Declared:
    name: str
    path: Path

    @property
    def module(self) -> ModuleType:
        return MODULES[self.name]

    @property
    def format_file(self) -> str:
        return "project.md" if self.name == PROJECT else project_register.REGISTERS[self.name]


def declared(project_dir: Path) -> list[Declared]:
    """The project register first, then the registers it lists; empty when no project register is declared.

    When PROJECT.md is missing or unreadable, only the project register is returned.
    """
    project_file = project_register.find_project_register(project_dir)
    if project_file is None:
        return []
    result = [Declared(PROJECT, project_file)]
    try:
        others = project_register.declared_registers(project_dir, project_file)
    except (OSError, ValueError):
        return result
    result += [Declared(name, path) for name, path in others.items() if name in MODULES]
    return result


def summary(project_dir: Path, today: date) -> Optional[str]:
    """One line of session context for every declared register, or None when the project declares none."""
    registers = declared(project_dir)
    if registers:
        parts = []
        for register in registers:
            label = _label(register.path, project_dir)
            try:
                line = register.module.summary_line(register.path, today, label=label)
            except (OSError, ValueError, ArithmeticError) as exc:
                line = f"{register.name} `{label}` cannot be read ({type(exc).__name__})"
            parts.append(line.rstrip("."))
        return "pm-skills: " + "; ".join(parts) + "."
    legacy = project_register.find_legacy_team_register(project_dir)
    if legacy is not None:
        return ("pm-skills: the team register is declared in the instruction file, as before pm-skills 1.0; "
                "registers are now listed in PROJECT.md: run /pm-skills:project-setup to migrate.")
    return None


def _label(path: Path, project_dir: Path) -> str:
    try:
        return str(path.relative_to(project_dir))
    except ValueError:
        return str(path)


def matching(project_dir: Path, edited: Path) -> Optional[Declared]:
    """The declared register that the edited file is, if any."""
    target = edited.resolve()
    for register in declared(project_dir):
        if register.path.resolve() == target:
            return register
    return None
