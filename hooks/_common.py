"""Helpers shared by the plugin's hook scripts. A hook never interrupts the session for its own errors."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(PLUGIN_ROOT / "shared" / "scripts"))


def read_payload() -> dict:
    payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        raise ValueError("hook input is not a JSON object")
    return payload


def project_dir(payload: dict) -> Optional[Path]:
    value = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd")
    return Path(value) if value else None


def emit(output: dict) -> None:
    print(json.dumps(output))


def fail_quietly(script: str, exc: BaseException) -> int:
    print(f"pm-skills {script}: {type(exc).__name__}: {exc}", file=sys.stderr)
    return 0
