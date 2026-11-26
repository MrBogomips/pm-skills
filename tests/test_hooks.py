from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from _support import FIXTURES, HOOKS, REPO, fixture_text

import project_register as pr
import registers
import teams_register as tr

FIXTURE = fixture_text()
TODAY = date(2026, 11, 23)
REGISTER_FILES = ("PROJECT.md", "TOOLS.md", "TEAMS.md", "TAILORING.md", "RISKS.md", "DECISIONS.md", "STAKEHOLDERS.md",
                  "CAPACITY.md", "CHANGES.md", "BUDGET.md", "SCHEDULE.md", "RACI.md", "GATES.md", "ACTIONS.md")


def make_project(tmp: str, declaration: str = "- Project register: `PROJECT.md`", files=REGISTER_FILES,
                 instructions: str = "AGENTS.md") -> Path:
    project = Path(tmp) / "project"
    project.mkdir()
    (project / instructions).write_text(f"# Rules\n\n## Working documents\n\n{declaration}\n", encoding="utf-8")
    for name in files:
        shutil.copy(FIXTURES / name, project / name)
    return project


def run_hook(script: str, project: Path, payload) -> subprocess.CompletedProcess:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project), "CLAUDE_PLUGIN_ROOT": str(REPO)}
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run([sys.executable, str(HOOKS / script)], input=stdin, env=env,
                          capture_output=True, text=True)


class FindProjectRegister(unittest.TestCase):
    def test_reads_agents_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, "- Project register: `pm/PROJECT.md`", files=())
            self.assertEqual(pr.find_project_register(project), project / "pm" / "PROJECT.md")

    def test_allows_trailing_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, "- Project register: `PROJECT.md` (authoritative)", files=())
            self.assertEqual(pr.find_project_register(project), project / "PROJECT.md")

    def test_ignores_fenced_example(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, "```markdown\n- Project register: `PROJECT.md`\n```", files=())
            self.assertIsNone(pr.find_project_register(project))

    def test_falls_back_to_claude_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, instructions="CLAUDE.md", files=())
            self.assertEqual(pr.find_project_register(project), project / "PROJECT.md")

    def test_none_without_instruction_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(pr.find_project_register(Path(tmp)))

    def test_finds_legacy_team_declaration(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, "- Team register: `TEAMS.md`", files=())
            self.assertIsNone(pr.find_project_register(project))
            self.assertEqual(pr.find_legacy_team_register(project), project / "TEAMS.md")


class Declared(unittest.TestCase):
    def test_project_first_then_listed_registers(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            names = [d.name for d in registers.declared(project)]
            self.assertEqual(names, ["Project register", "Tools register", "Team register", "Tailoring register",
                                     "Risk register", "Decision log", "Stakeholder register",
                                     "Capacity register", "Change log", "Budget register",
                                     "Schedule register", "RACI matrix", "Gate register", "Action log"])

    def test_missing_project_file_gives_project_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, files=())
            self.assertEqual([d.name for d in registers.declared(project)], ["Project register"])

    def test_nothing_declared(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(registers.declared(make_project(tmp, "- Reports: `report/`", files=())), [])


class SummaryLines(unittest.TestCase):
    def summary(self, text: str | None) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "TEAMS.md"
            if text is not None:
                path.write_text(text, encoding="utf-8")
            return tr.summary_line(path, TODAY, label="TEAMS.md")

    def test_team_recent(self):
        self.assertEqual(self.summary(FIXTURE), "Team register `TEAMS.md`: 3 active, last reconciled 2026-11-20.")

    def test_team_stale(self):
        text = FIXTURE.replace("Last reconciled: 2026-11-20", "Last reconciled: 2026-09-01")
        self.assertEqual(self.summary(text), "Team register `TEAMS.md`: 3 active, last reconciled 2026-09-01 "
                                             "(83 days ago: run /pm-skills:team-register to reconcile).")

    def test_team_never_reconciled(self):
        text = FIXTURE.replace("Last reconciled: 2026-11-20\n", "")
        self.assertEqual(self.summary(text), "Team register `TEAMS.md`: 3 active, never reconciled.")

    def test_team_invalid(self):
        text = FIXTURE.replace("| bok |", "| @bok |").replace("| web, ux |", "| a@b.io |")
        self.assertEqual(self.summary(text), "Team register `TEAMS.md` has 2 validation errors: "
                                             "run /pm-skills:team-register to fix them.")

    def test_team_missing(self):
        self.assertEqual(self.summary(None), "Team register `TEAMS.md` is declared but missing: "
                                             "run /pm-skills:team-register to create it.")

    def test_whole_project_in_one_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            line = registers.summary(make_project(tmp), TODAY)
        self.assertNotIn("\n", line)
        self.assertTrue(line.startswith("pm-skills: Project register `PROJECT.md`: Acme Portal (ACME), hybrid; "),
                        line)
        self.assertIn("Tools register `TOOLS.md`: 4 tools, 2 with write access", line)
        self.assertIn("Risk register `RISKS.md`: 3 open, 1 past their review date", line)
        self.assertIn("Decision log `DECISIONS.md`: 2 decisions, 1 in force, latest D-002 on 2026-09-18", line)
        self.assertIn("Stakeholder register `STAKEHOLDERS.md`: 3 active, 2 below their desired engagement, "
                      "1 past their review date", line)
        self.assertIn("Capacity register `CAPACITY.md`: 3 members with a base allocation, 2 periods starting in "
                      "the next 14 days, next day off 2026-12-08", line)
        self.assertIn("Change log `CHANGES.md`: 2 open (1 proposed, 1 assessed), 2 decided, "
                      "latest decision CR-002 on 2026-11-04", line)
        self.assertIn("Budget register `BUDGET.md`: budget 208100.00 EUR, reserves 18400.00 EUR "
                      "(contingency 8400.00, management reserve 10000.00), last reviewed 2026-11-20", line)
        self.assertIn("Schedule register `SCHEDULE.md`: source register, 10 activities, latest baseline B-02 "
                      "approved 2026-11-04", line)
        self.assertIn("RACI matrix `RACI.md`: 3 deliverables, 5 roles", line)
        self.assertIn("Gate register `GATES.md`: 2 gates (1 passed, 1 open), next G-002 planned 2026-11-27", line)
        self.assertIn("Action log `ACTIONS.md`: 3 open, 1 overdue, 1 due in the next 7 days", line)

    def test_missing_new_registers_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = tuple(f for f in REGISTER_FILES
                          if f not in ("STAKEHOLDERS.md", "CAPACITY.md", "CHANGES.md", "BUDGET.md", "SCHEDULE.md",
                                       "RACI.md", "GATES.md", "ACTIONS.md"))
            line = registers.summary(make_project(tmp, files=files), TODAY)
        self.assertIn("Stakeholder register `STAKEHOLDERS.md` is declared but missing: "
                      "run /pm-skills:stakeholder-register to create it", line)
        self.assertIn("Capacity register `CAPACITY.md` is declared but missing", line)
        self.assertIn("Change log `CHANGES.md` is declared but missing", line)
        self.assertIn("Budget register `BUDGET.md` is declared but missing: "
                      "run /pm-skills:budget-tracker to create it", line)
        self.assertIn("Schedule register `SCHEDULE.md` is declared but missing: "
                      "run /pm-skills:schedule-check to create it", line)
        self.assertIn("RACI matrix `RACI.md` is declared but missing: "
                      "run /pm-skills:raci-matrix to create it", line)
        self.assertIn("Gate register `GATES.md` is declared but missing: "
                      "run /pm-skills:phase-gate-review to create it", line)
        self.assertIn("Action log `ACTIONS.md` is declared but missing: "
                      "run /pm-skills:action-log to create it", line)

    def test_unreadable_register_does_not_hide_the_others(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            (project / "RISKS.md").unlink()
            (project / "RISKS.md").mkdir()
            line = registers.summary(project, TODAY)
        self.assertIn("Risk register `RISKS.md` cannot be read", line)
        self.assertIn("Team register `TEAMS.md`: 3 active", line)

    def test_legacy_declaration_suggests_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            line = registers.summary(make_project(tmp, "- Team register: `TEAMS.md`", files=("TEAMS.md",)), TODAY)
        self.assertIn("/pm-skills:project-setup", line)

    def test_silent_without_declaration(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(registers.summary(make_project(tmp, "- Reports: `report/`", files=()), TODAY))


class SessionStartHook(unittest.TestCase):
    payload = {"hook_event_name": "SessionStart", "source": "startup", "session_id": "s"}

    def test_silent_without_declaration(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_hook("session_start.py", make_project(tmp, "- Reports: `report/`", files=()), self.payload)
            self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_emits_one_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_hook("session_start.py", make_project(tmp), self.payload)
            self.assertEqual(result.returncode, 0)
            output = json.loads(result.stdout)["hookSpecificOutput"]
            self.assertEqual(output["hookEventName"], "SessionStart")
            context = output["additionalContext"]
            self.assertNotIn("\n", context)
            self.assertIn("Team register `TEAMS.md`: 3 active", context)
            self.assertIn("Tailoring register `TAILORING.md`", context)

    def test_reports_missing_project_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_hook("session_start.py", make_project(tmp, files=()), self.payload)
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("declared but missing", context)

    def test_bad_input_never_breaks_the_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_hook("session_start.py", make_project(tmp), "not json")
            self.assertEqual((result.returncode, result.stdout), (0, ""))
            self.assertIn("session_start", result.stderr)


class PostToolUseHook(unittest.TestCase):
    def payload(self, path: Path) -> dict:
        return {"hook_event_name": "PostToolUse", "tool_name": "Edit", "tool_input": {"file_path": str(path)}}

    def test_ignores_other_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            (project / "TEAMS.md").write_text(FIXTURE.replace("| bok |", "| @bok |"), encoding="utf-8")
            result = run_hook("check_register.py", project, self.payload(project / "README.md"))
            self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_silent_when_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            for name in REGISTER_FILES:
                result = run_hook("check_register.py", project, self.payload(project / name))
                self.assertEqual((name, result.returncode, result.stdout), (name, 0, ""))

    def test_reports_team_errors(self):
        bad_rows = "".join(f"| x{i} | X | Acme | @x{i} |  | dev |  |\n" for i in range(12))
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            (project / "TEAMS.md").write_text(FIXTURE.replace("\n## History", bad_rows + "\n## History"),
                                              encoding="utf-8")
            result = run_hook("check_register.py", project, self.payload(project / "TEAMS.md"))
            self.assertEqual(result.returncode, 0)
            output = json.loads(result.stdout)
            self.assertEqual(output["decision"], "block")
            reason = output["reason"]
            self.assertIn("line 12:", reason)
            self.assertIn("validation errors; fix them", reason)
            self.assertEqual(reason.count("\n- line "), 10)
            self.assertIn("teams.md", reason)

    def test_reports_project_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            text = (project / "PROJECT.md").read_text(encoding="utf-8").replace("hybrid", "waterfall")
            (project / "PROJECT.md").write_text(text, encoding="utf-8")
            result = run_hook("check_register.py", project, self.payload(project / "PROJECT.md"))
            output = json.loads(result.stdout)
            self.assertEqual(output["decision"], "block")
            self.assertIn("Delivery approach", output["reason"])
            self.assertIn("project.md", output["reason"])

    def test_reports_risk_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            text = (project / "RISKS.md").read_text(encoding="utf-8").replace("| 16 |", "| 12 |")
            (project / "RISKS.md").write_text(text, encoding="utf-8")
            result = run_hook("check_register.py", project, self.payload(project / "RISKS.md"))
            reason = json.loads(result.stdout)["reason"]
            self.assertIn("Score", reason)
            self.assertTrue(reason.startswith("RISKS.md has 1 validation error; fix them"), reason)

    def test_reports_errors_of_the_new_registers(self):
        cases = (("STAKEHOLDERS.md", "| high | high |", "| top | high |", "Interest", "stakeholders.md"),
                 ("CAPACITY.md", "| 80 |", "| 180 |", "Allocation", "capacity.md"),
                 ("CHANGES.md", "Status: proposed", "Status: open", "Status", "changes.md"),
                 ("BUDGET.md", "| labor |", "| people |", "Kind", "budget.md"),
                 ("SCHEDULE.md", "| A-004 SS+130 |", "| A-008 |", "cycle", "schedule.md"),
                 ("RACI.md", "| I | A | R | R | C |", "| I | C | R | R | C |", "exactly one A", "raci.md"),
                 ("GATES.md", "| 2026-11-27 | open |", "| 2026-11-27 | closed |", "Status", "gates.md"),
                 ("ACTIONS.md", "Status: open", "Status: wip", "Status", "actions.md"))
        for name, old, new, keyword, format_file in cases:
            with tempfile.TemporaryDirectory() as tmp:
                project = make_project(tmp)
                text = (project / name).read_text(encoding="utf-8").replace(old, new, 1)
                (project / name).write_text(text, encoding="utf-8")
                result = run_hook("check_register.py", project, self.payload(project / name))
                output = json.loads(result.stdout)
                self.assertEqual(output["decision"], "block", name)
                self.assertIn(keyword, output["reason"])
                self.assertIn(format_file, output["reason"])


if __name__ == "__main__":
    unittest.main()
