from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from _support import HOOKS, REPO, fixture_text

import teams_register as tr

FIXTURE = fixture_text()
TODAY = date(2026, 11, 23)


def make_project(tmp: str, declaration: str = "- Team register: `TEAMS.md`", register: str | None = FIXTURE,
                 instructions: str = "AGENTS.md") -> Path:
    project = Path(tmp) / "project"
    project.mkdir()
    (project / instructions).write_text(f"# Rules\n\n## Working documents\n\n{declaration}\n", encoding="utf-8")
    if register is not None:
        (project / "TEAMS.md").write_text(register, encoding="utf-8")
    return project


def run_hook(script: str, project: Path, payload) -> subprocess.CompletedProcess:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project), "CLAUDE_PLUGIN_ROOT": str(REPO)}
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run([sys.executable, str(HOOKS / script)], input=stdin, env=env,
                          capture_output=True, text=True)


class FindRegister(unittest.TestCase):
    def test_find_register_reads_agents_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, "- Team register: `team/TEAMS.md`")
            self.assertEqual(tr.find_register(project), project / "team" / "TEAMS.md")

    def test_find_register_allows_trailing_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, "- Team register: `TEAMS.md` (authoritative, committed)")
            self.assertEqual(tr.find_register(project), project / "TEAMS.md")

    def test_find_register_falls_back_to_claude_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, instructions="CLAUDE.md")
            self.assertEqual(tr.find_register(project), project / "TEAMS.md")

    def test_find_register_none_without_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, "- Reports: `report/`")
            self.assertIsNone(tr.find_register(project))

    def test_find_register_none_without_instruction_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(tr.find_register(Path(tmp)))


class SummaryLine(unittest.TestCase):
    def summary(self, text: str | None) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "TEAMS.md"
            if text is not None:
                path.write_text(text, encoding="utf-8")
            return tr.summary_line(path, TODAY, label="TEAMS.md")

    def test_summary_line_recent(self):
        self.assertEqual(self.summary(FIXTURE), "Team register `TEAMS.md`: 3 active, last reconciled 2026-11-20.")

    def test_summary_line_stale(self):
        text = FIXTURE.replace("Last reconciled: 2026-11-20", "Last reconciled: 2026-09-01")
        self.assertEqual(self.summary(text), "Team register `TEAMS.md`: 3 active, last reconciled 2026-09-01 "
                                             "(83 days ago: run /pm-skills:team-register to reconcile).")

    def test_summary_line_never_reconciled(self):
        text = FIXTURE.replace("Last reconciled: 2026-11-20\n", "")
        self.assertEqual(self.summary(text), "Team register `TEAMS.md`: 3 active, never reconciled.")

    def test_summary_line_invalid(self):
        text = FIXTURE.replace("| bok |", "| @bok |").replace("| web, ux |", "| a@b.io |")
        self.assertEqual(self.summary(text), "Team register `TEAMS.md` has 2 validation errors: "
                                             "run /pm-skills:team-register to fix them.")

    def test_summary_line_missing(self):
        self.assertEqual(self.summary(None), "Team register `TEAMS.md` is declared but missing: "
                                             "run /pm-skills:team-register to create it.")


class SessionStartHook(unittest.TestCase):
    payload = {"hook_event_name": "SessionStart", "source": "startup", "session_id": "s"}

    def test_session_start_silent_without_declaration(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_hook("session_start.py", make_project(tmp, "- Reports: `report/`"), self.payload)
            self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_session_start_emits_one_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_hook("session_start.py", make_project(tmp), self.payload)
            self.assertEqual(result.returncode, 0)
            output = json.loads(result.stdout)["hookSpecificOutput"]
            self.assertEqual(output["hookEventName"], "SessionStart")
            context = output["additionalContext"]
            self.assertNotIn("\n", context)
            self.assertTrue(context.startswith("Team register `TEAMS.md`: 3 active"), context)

    def test_session_start_reports_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_hook("session_start.py", make_project(tmp, register=None), self.payload)
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("declared but missing", context)


class PostToolUseHook(unittest.TestCase):
    def payload(self, path: Path) -> dict:
        return {"hook_event_name": "PostToolUse", "tool_name": "Edit", "tool_input": {"file_path": str(path)}}

    def test_post_tool_use_ignores_other_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, register=FIXTURE.replace("| bok |", "| @bok |"))
            result = run_hook("check_register.py", project, self.payload(project / "README.md"))
            self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_post_tool_use_silent_when_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            result = run_hook("check_register.py", project, self.payload(project / "TEAMS.md"))
            self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_post_tool_use_reports_errors(self):
        bad_rows = "".join(f"| x{i} | X | Acme | @x{i} |  | dev |  |\n" for i in range(12))
        text = FIXTURE.replace("\n## History", bad_rows + "\n## History")
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, register=text)
            result = run_hook("check_register.py", project, self.payload(project / "TEAMS.md"))
            self.assertEqual(result.returncode, 0)
            output = json.loads(result.stdout)
            self.assertEqual(output["decision"], "block")
            reason = output["reason"]
            self.assertIn("line 13:", reason)
            self.assertEqual(reason.count("\n- line "), 10)
            self.assertIn("and 14 more", reason)
            self.assertIn("shared/registers/teams.md", reason)

    def test_post_tool_use_matches_symlinked_project_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, register=FIXTURE.replace("| bok |", "| @bok |"))
            link = Path(tmp) / "link"
            link.symlink_to(project)
            result = run_hook("check_register.py", link, self.payload(project.resolve() / "TEAMS.md"))
            self.assertEqual(json.loads(result.stdout)["decision"], "block")


class MalformedInput(unittest.TestCase):
    def test_hooks_survive_malformed_stdin(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            for script in ("session_start.py", "check_register.py"):
                result = run_hook(script, project, "{ not json")
                self.assertEqual((result.returncode, result.stdout), (0, ""), script)
                self.assertTrue(result.stderr, script)


if __name__ == "__main__":
    unittest.main()
