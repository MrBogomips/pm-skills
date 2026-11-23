#!/usr/bin/env python3
"""SessionStart: one line of context about the project's team register; silent when none is declared."""
from __future__ import annotations

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402


def main() -> int:
    try:
        import teams_register

        project = _common.project_dir(_common.read_payload())
        register = teams_register.find_register(project) if project else None
        if register is None:
            return 0
        label = os.path.relpath(register, project)
        _common.emit({"hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": teams_register.summary_line(register, date.today(), label=label),
        }})
        return 0
    except Exception as exc:  # a hook must never break the session
        return _common.fail_quietly("session_start", exc)


if __name__ == "__main__":
    sys.exit(main())
