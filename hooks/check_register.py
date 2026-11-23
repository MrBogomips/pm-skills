#!/usr/bin/env python3
"""PostToolUse on Write/Edit: validate the team register when the edited file is the declared one."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402

MAX_ERRORS_SHOWN = 10


def report(label: str, errors: list[str]) -> str:
    lines = [f"{label} has {len(errors)} validation errors; fix them before going on:"]
    lines += [f"- {error}" for error in errors[:MAX_ERRORS_SHOWN]]
    if len(errors) > MAX_ERRORS_SHOWN:
        lines.append(f"… and {len(errors) - MAX_ERRORS_SHOWN} more")
    lines.append(f"The format is in {_common.PLUGIN_ROOT / 'shared' / 'registers' / 'teams.md'}.")
    return "\n".join(lines)


def main() -> int:
    try:
        import teams_register

        payload = _common.read_payload()
        edited = (payload.get("tool_input") or {}).get("file_path")
        project = _common.project_dir(payload)
        register = teams_register.find_register(project) if project and edited else None
        if register is None or Path(edited).resolve() != register.resolve():
            return 0
        errors = teams_register.validate(register.read_text(encoding="utf-8"))
        if errors:
            label = os.path.relpath(register, project)
            _common.emit({"decision": "block", "reason": report(label, errors)})
        return 0
    except Exception as exc:  # a hook must never break the session
        return _common.fail_quietly("check_register", exc)


if __name__ == "__main__":
    sys.exit(main())
