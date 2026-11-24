#!/usr/bin/env python3
"""SessionStart: one line of context about the project's declared registers; silent when none is declared."""
from __future__ import annotations

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402


def main() -> int:
    try:
        import registers

        project = _common.project_dir(_common.read_payload())
        line = registers.summary(project, date.today()) if project else None
        if line is None:
            return 0
        _common.emit({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": line}})
        return 0
    except Exception as exc:  # a hook must never break the session
        return _common.fail_quietly("session_start", exc)


if __name__ == "__main__":
    sys.exit(main())
