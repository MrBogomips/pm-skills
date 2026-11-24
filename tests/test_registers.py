"""Tests of the project, tools, tailoring, risk and decision registers and of document naming."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from _support import REPO, SCRIPTS, fixture_text

import decisions_register as dr
import doc_naming as dn
import project_register as pr
import risks_register as rr
import tailoring_register as tl
import tools_register as tr

PROJECT = fixture_text("PROJECT.md")
TOOLS = fixture_text("TOOLS.md")
TAILORING = fixture_text("TAILORING.md")
RISKS = fixture_text("RISKS.md")
DECISIONS = fixture_text("DECISIONS.md")
POINTS = {"risk-register": ("format", "scale", "rules", "terms"), "status-report": ("format", "steps", "terms"),
          "team-register": ()}


def replaced(text: str, old: str, new: str) -> str:
    assert old in text, old
    return text.replace(old, new, 1)


class ErrorAssertions(unittest.TestCase):
    def assertError(self, errors: list[str], line: int, keyword: str) -> None:
        matching = [e for e in errors if e.startswith(f"line {line}:") and keyword in e]
        self.assertTrue(matching, f"no 'line {line}: …{keyword}…' in {errors}")


class ProjectRegister(ErrorAssertions):
    def test_fixture_is_valid(self):
        self.assertEqual(pr.validate(PROJECT), [])

    def test_parse_values_and_registers(self):
        project, _ = pr.parse(PROJECT)
        self.assertEqual(project.get("Identity", "Internal code"), "ACME")
        self.assertEqual(project.registers()["Risk register"], "RISKS.md")
        self.assertEqual(project.type_codes(), {"status-report": "SAL"})

    def test_minimal_register_with_empty_sections(self):
        text = "# Project\n\n## Identity\n\n- Project name: Acme Portal\n\n## Profile\n\n## Conventions\n\n## Registers\n"
        self.assertEqual(pr.validate(text), [])

    def test_rejects_missing_section(self):
        errors = pr.validate(PROJECT.split("## Registers")[0])
        self.assertTrue(any("missing section '## Registers'" in e for e in errors), errors)

    def test_rejects_sections_out_of_order(self):
        text = replaced(PROJECT, "## Registers", "## Identity")
        self.assertError(pr.validate(text), 28, "unexpected section")

    def test_rejects_unknown_key(self):
        self.assertError(pr.validate(replaced(PROJECT, "- Sprint length: 2", "- Velocity: 30")), 19, "unknown key")

    def test_rejects_bad_enum(self):
        self.assertError(pr.validate(replaced(PROJECT, "hybrid", "waterfall")), 16, "Delivery approach")

    def test_rejects_end_before_start(self):
        self.assertError(pr.validate(replaced(PROJECT, "2026-12-18", "2025-12-18")), 10, "before Start date")

    def test_rejects_coded_without_internal_code(self):
        self.assertError(pr.validate(replaced(PROJECT, "- Internal code: ACME\n", "")), 23, "Internal code")

    def test_rejects_bad_type_code(self):
        self.assertError(pr.validate(replaced(PROJECT, "status-report=SAL", "status report=sal")), 25, "Type codes")

    def test_rejects_unknown_register(self):
        self.assertError(pr.validate(replaced(PROJECT, "- Decision log:", "- RAID log:")), 34, "unknown key")

    def test_rejects_register_without_backticks(self):
        self.assertError(pr.validate(replaced(PROJECT, "`RISKS.md`", "RISKS.md")), 33, "backticks")

    def test_rejects_shared_file(self):
        self.assertError(pr.validate(replaced(PROJECT, "`DECISIONS.md`", "`RISKS.md`")), 34, "same file")

    def test_rejects_duplicate_and_empty(self):
        errors = pr.validate(replaced(PROJECT, "- Client: Acme Corp\n", "- Client: Acme Corp\n- Client:\n"))
        self.assertError(errors, 6, "already on line 5")

    def test_rejects_free_text_and_contacts(self):
        errors = pr.validate(replaced(PROJECT, "- Client: Acme Corp", "Some notes\n- Client: ops@acme.example"))
        self.assertError(errors, 5, "unexpected content")
        self.assertError(errors, 6, "email")


class ToolsRegister(ErrorAssertions):
    def test_fixture_is_valid(self):
        tools, errors = tr.parse(TOOLS)
        self.assertEqual(errors, [])
        self.assertEqual(tools[1].purposes, ("code", "ci", "releases"))
        self.assertEqual((tools[0].access_kind, tools[0].access_target), ("mcp", "atlassian"))

    def test_rejects_unknown_purpose(self):
        self.assertError(tr.validate(replaced(TOOLS, "| issues |", "| tickets |")), 5, "capability")

    def test_rejects_bad_access(self):
        self.assertError(tr.validate(replaced(TOOLS, "`mcp:atlassian`", "atlassian")), 5, "Access")

    def test_rejects_bad_mode(self):
        self.assertError(tr.validate(replaced(TOOLS, "| project ACME | write |", "| project ACME | admin |")), 5,
                         "Mode")

    def test_rejects_duplicate_and_extra_content(self):
        row = "| Jira | issues | `mcp:atlassian` | project ACME | write |"
        errors = tr.validate(replaced(TOOLS, row, row + "\n" + row) + "\nNotes here\n")
        self.assertError(errors, 6, "duplicate")
        self.assertError(errors, 11, "unexpected content")

    def test_rejects_missing_table(self):
        self.assertTrue(any("missing the tools table" in e for e in tr.validate("# Tools\n")))


class TailoringRegister(ErrorAssertions):
    def test_fixture_is_valid(self):
        rules, errors = tl.parse(TAILORING, POINTS)
        self.assertEqual(errors, [])
        self.assertEqual(rules, {"risk-register": {"scale": 1}, "status-report": {"format": 1, "terms": 1}})

    def test_fixture_is_valid_against_the_plugin(self):
        self.assertEqual(tl.validate(TAILORING), [])

    def test_rejects_unknown_skill(self):
        self.assertError(tl.parse(replaced(TAILORING, "## risk-register", "## risk-log"), POINTS)[1], 3, "not a skill")

    def test_rejects_skill_without_points(self):
        text = TAILORING + "\n## team-register\n\n### terms\n\n- x\n"
        self.assertError(tl.parse(text, POINTS)[1], 19, "declares no extension points")

    def test_rejects_point_outside_vocabulary(self):
        self.assertError(tl.parse(replaced(TAILORING, "### scale", "### colors"), POINTS)[1], 5, "not an extension point")

    def test_rejects_undeclared_point(self):
        self.assertError(tl.parse(replaced(TAILORING, "### format", "### scale"), POINTS)[1], 11, "does not declare")

    def test_rejects_point_without_rules_and_loose_text(self):
        errors = tl.parse(replaced(TAILORING, "## status-report\n", "## status-report\n\nloose text\n"), POINTS)[1]
        self.assertError(errors, 11, "unexpected content")

    def test_rejects_empty_point(self):
        text = replaced(TAILORING, "- The status report is called \"SAL\" in titles.\n", "")
        self.assertError(tl.parse(text, POINTS)[1], 15, "has no rule")

    def test_declared_points_reads_the_skills(self):
        points = tl.declared_points(REPO)
        self.assertIn("risk-register", points)
        self.assertTrue(set(points["risk-register"]) <= set(tl.POINTS))


class RiskRegister(ErrorAssertions):
    def test_fixture_is_valid(self):
        register, errors = rr.parse(RISKS)
        self.assertEqual(errors, [])
        self.assertEqual(register.scale, (1, 5))
        self.assertEqual([r.id for r in register.risks], ["R-001", "R-002", "R-003", "R-004"])

    def test_rejects_wrong_score(self):
        self.assertError(rr.validate(replaced(RISKS, "| 16 |", "| 12 |")), 8, "Score")

    def test_rejects_value_outside_scale(self):
        self.assertError(rr.validate(replaced(RISKS, "Scale: 1-5", "Scale: 1-3")), 8, "Probability")

    def test_rejects_strategy_of_the_other_type(self):
        self.assertError(rr.validate(replaced(RISKS, "| enhance |", "| mitigate |")), 10, "Strategy")

    def test_open_risk_needs_owner_and_review(self):
        errors = rr.validate(replaced(RISKS, "| bo-k | open | 2026-11-02 | 2026-12-10 |", "|  | open | 2026-11-02 |  |"))
        self.assertError(errors, 10, "needs Owner")
        self.assertError(errors, 10, "needs Review")

    def test_rejects_duplicate_id_and_bad_status(self):
        errors = rr.validate(replaced(replaced(RISKS, "| R-002 |", "| R-001 |"), "| closed |", "| done |"))
        self.assertError(errors, 9, "duplicate ID")
        self.assertError(errors, 11, "Status")

    def test_rejects_bad_scale_and_contacts(self):
        errors = rr.validate(replaced(replaced(RISKS, "Scale: 1-5", "Scale: 5"), "| Tech lead |", "| tl@acme.example |"))
        self.assertError(errors, 3, "Scale")
        self.assertError(errors, 9, "email")

    def test_summary_counts_open_and_overdue(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "RISKS.md"
            path.write_text(RISKS, encoding="utf-8")
            self.assertEqual(rr.summary_line(path, date(2026, 11, 23)), "Risk register `RISKS.md`: 3 open, 1 past "
                             "their review date: run /pm-skills:risk-register to review them.")
            self.assertEqual(rr.summary_line(path, date(2026, 11, 1)), "Risk register `RISKS.md`: 3 open.")


class DecisionLog(ErrorAssertions):
    def test_fixture_is_valid(self):
        decisions, errors = dr.parse(DECISIONS)
        self.assertEqual(errors, [])
        self.assertEqual([d.id for d in decisions], ["D-001", "D-002"])
        self.assertEqual(decisions[1].date, date(2026, 9, 18))

    def test_empty_log_is_valid(self):
        self.assertEqual(dr.validate("# Decisions\n"), [])

    def test_rejects_missing_required_key(self):
        self.assertError(dr.validate(replaced(DECISIONS, "- Decided by: Tech lead\n", "")), 3, "Decided by")

    def test_rejects_bad_heading_and_unknown_key(self):
        errors = dr.validate(replaced(replaced(DECISIONS, "## D-001 Background", "## Background"),
                                      "- Consequences:", "- Notes:"))
        self.assertError(errors, 3, "heading")
        self.assertError(errors, 20, "unknown key")

    def test_rejects_one_sided_supersession(self):
        self.assertError(dr.validate(replaced(DECISIONS, "- Supersedes: D-001\n", "")), 11, "Supersedes: D-001")

    def test_rejects_superseded_without_successor(self):
        errors = dr.validate(replaced(replaced(DECISIONS, "- Superseded by: D-002\n", ""), "- Supersedes: D-001\n", ""))
        self.assertError(errors, 3, "Superseded by")

    def test_rejects_out_of_order_and_bad_status(self):
        errors = dr.validate(replaced(replaced(DECISIONS, "## D-002", "## D-000"), "Status: accepted", "Status: open"))
        self.assertError(errors, 13, "ID order")
        self.assertError(errors, 16, "Status")


class DocumentNaming(unittest.TestCase):
    def project(self, **changes: str) -> pr.Project:
        text = PROJECT
        for old, new in changes.items():
            text = replaced(text, old.replace("_", " "), new)
        project, errors = pr.parse(text)
        self.assertEqual(errors, [])
        return project

    def test_coded_numbers_per_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "ACME-SAL-001.md").write_text("x")
            (base / "ACME-SAL-007-steering.md").write_text("x")
            (base / "ACME-MM-002.md").write_text("x")
            project = self.project()
            self.assertEqual(dn.next_name(project, base, "status-report", date(2026, 11, 24)), "ACME-SAL-008.md")
            self.assertEqual(dn.next_name(project, base, "meeting-minutes", date(2026, 11, 24), "Kick off!"),
                             "ACME-MM-003-kick-off.md")

    def test_by_date_and_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = self.project(**{"- Naming: coded": "- Naming: by date"})
            name = dn.next_name(project, base, "status-report", date(2026, 11, 24))
            self.assertEqual(name, "status-report/2026-11-24-status-report.md")
            (base / "status-report").mkdir()
            (base / name).write_text("x")
            with self.assertRaises(FileExistsError):
                dn.next_name(project, base, "status-report", date(2026, 11, 24))

    def test_version_in_name_with_plus_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = self.project(**{"- Version in file name: no": "- Version in file name: yes"})
            (base / "ACME-SAL-001-1.0.0.md").write_text("x")
            self.assertEqual(dn.next_name(project, base, "status-report", date(2026, 11, 24), version="1.0.0"),
                             "ACME-SAL-002-1.0.0.md")
            with self.assertRaises(dn.NamingError):
                dn.next_name(project, base, "status-report", date(2026, 11, 24))

    def test_plus_suffix_when_the_versioned_name_is_taken(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = self.project(**{"- Naming: coded": "- Naming: by date",
                                      "- Version in file name: no": "- Version in file name: yes"})
            (base / "status-report").mkdir()
            (base / "status-report/2026-11-24-status-report-1.0.0.md").write_text("x")
            self.assertEqual(dn.next_name(project, base, "status-report", date(2026, 11, 24), version="1.0.0"),
                             "status-report/2026-11-24-status-report-1.0.0+1.md")

    def test_unknown_type_code(self):
        with self.assertRaises(dn.NamingError):
            dn.next_name(self.project(), Path("."), "vendor-memo", date(2026, 11, 24))

    def test_bump(self):
        self.assertEqual([dn.bump("1.2.3", p) for p in ("major", "minor", "patch")], ["2.0.0", "1.3.0", "1.2.4"])
        with self.assertRaises(dn.NamingError):
            dn.bump("1.2", "patch")


class CommandLines(unittest.TestCase):
    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, text=True)

    def test_validate_exit_codes(self):
        cases = (("project_register.py", PROJECT, "hybrid", "waterfall"), ("tools_register.py", TOOLS, "read", "rw"),
                 ("risks_register.py", RISKS, "| 16 |", "| 1 |"),
                 ("decisions_register.py", DECISIONS, "accepted", "maybe"))
        with tempfile.TemporaryDirectory() as tmp:
            for script, good, old, new in cases:
                ok, bad = Path(tmp) / "ok.md", Path(tmp) / "bad.md"
                ok.write_text(good, encoding="utf-8")
                bad.write_text(replaced(good, old, new), encoding="utf-8")
                self.assertEqual(self.run_script(script, "validate", str(ok)).returncode, 0, script)
                self.assertEqual(self.run_script(script, "validate", str(bad)).returncode, 1, script)
                self.assertEqual(self.run_script(script, "validate", str(Path(tmp) / "none.md")).returncode, 2)
                self.assertEqual(self.run_script(script).returncode, 2)

    def test_doc_naming_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "PROJECT.md"
            project.write_text(PROJECT, encoding="utf-8")
            result = self.run_script("doc_naming.py", "next", "--project", str(project), "--dir", tmp,
                                     "--type", "status-report", "--date", "2026-11-24")
            self.assertEqual((result.returncode, result.stdout.strip()), (0, "ACME-SAL-001.md"))
            self.assertEqual(self.run_script("doc_naming.py", "bump", "0.9.1", "minor").stdout.strip(), "0.10.0")
            self.assertEqual(self.run_script("doc_naming.py", "bump", "x", "minor").returncode, 2)

    def test_tailoring_points_cli(self):
        result = self.run_script("tailoring_register.py", "points")
        self.assertEqual(result.returncode, 0)
        self.assertIn("risk-register:", result.stdout)


if __name__ == "__main__":
    unittest.main()
