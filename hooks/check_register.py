#!/usr/bin/env python3
"""PostToolUse on Write/Edit: validate the edited file when it is one of the project's declared registers."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402

MAX_ERRORS_SHOWN = 10


def report(label: str, format_file: str, errors: list[str]) -> str:
    lines = [f"{label} has {len(errors)} validation errors; fix them before going on:"]
    lines += [f"- {error}" for error in errors[:MAX_ERRORS_SHOWN]]
    if len(errors) > MAX_ERRORS_SHOWN:
        lines.append(f"… and {len(errors) - MAX_ERRORS_SHOWN} more")
    lines.append(f"The format is in {_common.PLUGIN_ROOT / 'shared' / 'registers' / format_file}.")
    return "\n".join(lines)


def main() -> int:
    try:
        import registers

        payload = _common.read_payload()
        edited = (payload.get("tool_input") or {}).get("file_path")
        project = _common.project_dir(payload)
        if not (project and edited):
            return 0
        register = registers.matching(project, Path(edited))
        if register is None:
            return 0
        errors = register.module.validate(register.path.read_text(encoding="utf-8"))
        if errors:
            label = os.path.relpath(register.path, project)
            _common.emit({"decision": "block", "reason": report(label, register.format_file, errors)})
        return 0
    except Exception as exc:  # a hook must never break the session
        return _common.fail_quietly("check_register", exc)


if __name__ == "__main__":
    sys.exit(main())
