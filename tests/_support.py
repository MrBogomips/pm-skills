"""Shared helpers for the tests: paths and import of the shared scripts."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURES = REPO / "tests" / "fixtures"
SCRIPTS = REPO / "shared" / "scripts"
HOOKS = REPO / "hooks"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def fixture_text(name: str = "TEAMS.md") -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")
