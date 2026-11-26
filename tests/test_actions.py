"""Tests of the action log (ACTIONS.md), its hook coverage and the PM backlog view."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from _support import FIXTURES, SCRIPTS, fixture_text

import actions_register as ar
import pm_backlog as pb
import project_register as pr
import registers

ACTIONS = fixture_text("ACTIONS.md")
TODAY = date(2026, 11, 23)
FILES = ("PROJECT.md", "TOOLS.md", "TEAMS.md", "TAILORING.md", "RISKS.md", "DECISIONS.md", "STAKEHOLDERS.md",
         "CAPACITY.md", "CHANGES.md", "BUDGET.md", "SCHEDULE.md", "RACI.md", "GATES.md", "ACTIONS.md")


def replaced(text: str, old: str, new: str) -> str:
    assert old in text, old
    return text.replace(old, new, 1)


def make_project(tmp: str, files=FILES) -> Path:
    project = Path(tmp) / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("# Rules\n\n- Project register: `PROJECT.md`\n", encoding="utf-8")
    for name in files:
        shutil.copy(FIXTURES / name, project / name)
    return project


class ErrorAssertions(unittest.TestCase):
    def assertError(self, errors: list[str], line: int, keyword: str) -> None:
        matching = [e for e in errors if e.startswith(f"line {line}:") and keyword in e]
        self.assertTrue(matching, f"no 'line {line}: ...{keyword}...' in {errors}")


class ActionLog(ErrorAssertions):
    def test_fixture_is_valid(self):
        actions, errors = ar.parse(ACTIONS)
        self.assertEqual(errors, [])
        self.assertEqual([a.id for a in actions], ["AC-001", "AC-002", "AC-003", "AC-004", "AC-005"])
        self.assertEqual(actions[2].due, date(2026, 11, 20))
        self.assertEqual(actions[2].fields["Item"], "ACME-142")

    def test_title_only_is_valid(self):
        self.assertEqual(ar.validate("# Actions\n"), [])

    def test_missing_title(self):
        self.assertError(ar.validate(replaced(ACTIONS, "# Actions", "# Todo")), 1, "title")

    def test_free_text_is_rejected(self):
        self.assertError(ar.validate(ACTIONS + "\nsome note\n"), len(ACTIONS.splitlines()) + 2, "unexpected content")

    def test_heading_must_use_ac_prefix(self):
        self.assertError(ar.validate(replaced(ACTIONS, "## AC-002", "## A-002")), 15, "heading")

    def test_unknown_key(self):
        self.assertError(ar.validate(replaced(ACTIONS, "- Owner: ada-l", "- Assignee: ada-l")), 27, "unknown key")

    def test_duplicate_key(self):
        self.assertError(ar.validate(replaced(ACTIONS, "- Owner: ada-l", "- Owner: ada-l\n- Owner: bo-k")),
                         28, "already on line 27")

    def test_empty_value(self):
        self.assertError(ar.validate(replaced(ACTIONS, "- Raised by: cy-t", "- Raised by:")), 32, "empty")

    def test_required_keys(self):
        for key in ("Raised", "Owner", "Status", "Action", "Source"):
            lines = ACTIONS.splitlines()
            start = lines.index("## AC-003 Fix the flaky login test")
            text = "\n".join(l for i, l in enumerate(lines) if not (i > start and l.startswith(f"- {key}:"))
                             or i > start + 12) + "\n"
            self.assertTrue(any(f"AC-003 needs '{key}'" in e for e in ar.validate(text)), key)

    def test_missing_owner_reported_on_heading(self):
        text = replaced(ACTIONS, "- Owner: ada-l\n", "")
        self.assertError(ar.validate(text), 24, "AC-003 needs 'Owner'")

    def test_open_needs_due(self):
        text = replaced(ACTIONS, "- Due: 2026-11-25\n", "")
        self.assertError(ar.validate(text), 15, "AC-002 needs 'Due'")

    def test_done_without_due_is_valid(self):
        self.assertEqual(ar.validate(replaced(ACTIONS, "- Due: 2026-11-10\n", "")), [])

    def test_status_must_be_known(self):
        self.assertError(ar.validate(replaced(ACTIONS, "- Status: open\n- Due: 2026-11-25", "- Status: wip\n- Due: 2026-11-25")),
                         19, "Status")

    def test_closed_required_for_done_and_dropped(self):
        self.assertError(ar.validate(replaced(ACTIONS, "- Closed: 2026-11-09\n", "")), 3, "AC-001 needs 'Closed'")
        self.assertError(ar.validate(replaced(ACTIONS, "- Closed: 2026-11-16\n", "")), 46, "AC-005 needs 'Closed'")

    def test_closed_only_when_done_or_dropped(self):
        text = replaced(ACTIONS, "- Due: 2026-11-25\n", "- Due: 2026-11-25\n- Closed: 2026-11-24\n")
        self.assertError(ar.validate(text), 21, "only a done or dropped action has 'Closed'")

    def test_outcome_only_when_closed(self):
        text = replaced(ACTIONS, "- Due: 2026-11-25\n", "- Due: 2026-11-25\n- Outcome: nothing yet\n")
        self.assertError(ar.validate(text), 21, "only a done or dropped action has 'Outcome'")

    def test_dates_must_be_dates_and_ordered(self):
        self.assertError(ar.validate(replaced(ACTIONS, "- Due: 2026-11-25", "- Due: 25/11/2026")), 20, "not a date")
        self.assertError(ar.validate(replaced(ACTIONS, "- Due: 2026-11-25", "- Due: 2026-11-10")), 20,
                         "before Raised")
        self.assertError(ar.validate(replaced(ACTIONS, "- Closed: 2026-11-09", "- Closed: 2026-11-01")), 12,
                         "before Raised")

    def test_tool_and_item_come_together(self):
        self.assertError(ar.validate(replaced(ACTIONS, "- Item: ACME-142\n", "")), 24, "Tool and Item")
        self.assertError(ar.validate(replaced(ACTIONS, "- Tool: Jira\n", "")), 24, "Tool and Item")

    def test_ids_unique_increasing_never_reused(self):
        self.assertError(ar.validate(replaced(ACTIONS, "## AC-003", "## AC-002")), 24, "duplicate ID")
        self.assertError(ar.validate(replaced(ACTIONS, "## AC-004", "## AC-001")), 36, "duplicate ID")
        self.assertError(ar.validate(replaced(ACTIONS, "## AC-004", "## AC-0")), 36, "heading")
        swapped = replaced(replaced(ACTIONS, "## AC-002", "## AC-009"), "## AC-003", "## AC-004")
        self.assertError(ar.validate(swapped), 24, "ID order")

    def test_contacts_are_rejected(self):
        self.assertError(ar.validate(replaced(ACTIONS, "- Owner: ada-l", "- Owner: ada@acme.io")), 27, "email")
        self.assertError(ar.validate(replaced(ACTIONS, "- Raised by: sponsor", "- Raised by: +39 02 1234 5678")),
                         44, "phone")

    def test_non_ascii_digits_are_rejected(self):
        self.assertNotEqual(ar.validate(replaced(ACTIONS, "## AC-001", "## AC-٠٠١")), [])

    def test_source_may_hold_digits_and_paths(self):
        self.assertEqual(ar.validate(replaced(ACTIONS, "- Source: request from the sponsor in the weekly status call",
                                              "- Source: request of 2026-11-20 in call 123 456 7890")), [])


class SummaryLine(unittest.TestCase):
    def summary(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ACTIONS.md"
            if text is not None:
                path.write_text(text, encoding="utf-8")
            return ar.summary_line(path, TODAY, label="ACTIONS.md")

    def test_counts_open_overdue_and_due_this_week(self):
        self.assertEqual(self.summary(ACTIONS), "Action log `ACTIONS.md`: 3 open, 1 overdue, 1 due in the next "
                                                "7 days: run /pm-skills:action-log to review them.")

    def test_nothing_overdue(self):
        text = replaced(ACTIONS, "- Due: 2026-11-20", "- Due: 2026-12-20")
        self.assertEqual(self.summary(text), "Action log `ACTIONS.md`: 3 open, 1 due in the next 7 days.")

    def test_none_open(self):
        self.assertEqual(self.summary("# Actions\n"), "Action log `ACTIONS.md`: no open actions.")

    def test_invalid_and_missing(self):
        self.assertEqual(self.summary(replaced(ACTIONS, "Status: open", "Status: wip")),
                         "Action log `ACTIONS.md` has 1 validation error: run /pm-skills:action-log to fix them.")
        self.assertEqual(self.summary(None), "Action log `ACTIONS.md` is declared but missing: "
                                             "run /pm-skills:action-log to create it.")


class Registration(unittest.TestCase):
    def test_declared_in_project_register(self):
        self.assertEqual(pr.REGISTERS["Action log"], "actions.md")
        self.assertEqual(pr.validate(fixture_text("PROJECT.md")), [])

    def test_registered_for_the_hooks(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            names = [d.name for d in registers.declared(project)]
            self.assertEqual(names[-1], "Action log")
            line = registers.summary(project, TODAY)
            self.assertIn("Action log `ACTIONS.md`: 3 open, 1 overdue", line)
            match = registers.matching(project, project / "ACTIONS.md")
            self.assertEqual((match.name, match.format_file), ("Action log", "actions.md"))

    def test_format_file_names_the_keeper(self):
        text = (SCRIPTS.parent / "registers" / "actions.md").read_text(encoding="utf-8")
        self.assertIn("Kept by: `action-log`.", text)


class Backlog(unittest.TestCase):
    def build(self, owners=(pb.PM_ROLE,), horizon=None, files=FILES, mutate=None):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, files)
            if mutate:
                mutate(project)
            return pb.build(project / "PROJECT.md", owners, TODAY, horizon)

    def origins(self, backlog):
        return [i.origin for i in backlog.items]

    def test_pm_view_sorted_by_due_date_then_undated(self):
        backlog = self.build()
        self.assertEqual(self.origins(backlog), ["AC-002", "G-002", "AC-004", "S-001", "CR-002", "CR-003"])
        self.assertEqual(backlog.notes, [])

    def test_days_until_due_negative_when_overdue(self):
        backlog = self.build(owners=("ada-l",))
        self.assertEqual([(i.origin, i.days) for i in backlog.items][:2], [("AC-003", -3), ("R-001", 8)])

    def test_horizon_keeps_overdue_and_undated(self):
        backlog = self.build(horizon=7)
        self.assertEqual(self.origins(backlog), ["AC-002", "G-002", "CR-002", "CR-003"])
        backlog = self.build(owners=("ada-l",), horizon=3)
        self.assertEqual(self.origins(backlog), ["AC-003"])

    def test_closed_actions_are_not_listed(self):
        self.assertNotIn("AC-001", self.origins(self.build(owners=pb.ALL)))
        self.assertNotIn("AC-005", self.origins(self.build(owners=pb.ALL)))

    def test_all_owners(self):
        origins = self.origins(self.build(owners=pb.ALL))
        for expected in ("AC-003", "R-001", "R-002", "R-003", "S-002", "S-003", "CR-003"):
            self.assertIn(expected, origins)
        self.assertNotIn("CR-004", origins)
        self.assertNotIn("CR-001", origins)
        self.assertNotIn("S-004", origins)
        self.assertNotIn("R-004", origins)

    def test_owner_other_than_pm_gets_no_change_requests_or_gates(self):
        origins = self.origins(self.build(owners=("bo-k",)))
        self.assertEqual(origins, ["S-002", "R-003"])

    def test_owner_match_is_case_insensitive(self):
        self.assertEqual(self.origins(self.build(owners=("ADA-L",))), ["AC-003", "R-001", "S-003"])

    def test_linked_work_item_is_shown(self):
        item = [i for i in self.build(owners=("ada-l",)).items if i.origin == "AC-003"][0]
        self.assertIn("Jira ACME-142", item.what)

    def test_conditions_of_go_with_conditions_are_listed(self):
        def mutate(project):
            path = project / "GATES.md"
            text = replaced(fixture_text("GATES.md"), "| G-001 | 2026-03-13 | go | steering committee |  |",
                            "| G-001 | 2026-03-13 | go with conditions | steering committee | Security review by April |")
            path.write_text(text, encoding="utf-8")
        backlog = self.build(mutate=mutate)
        item = [i for i in backlog.items if i.origin == "G-001"]
        self.assertEqual(len(item), 1)
        self.assertIn("Security review by April", item[0].what)
        self.assertIsNone(item[0].due)

    def test_invalid_or_missing_registers_are_noted_not_hidden(self):
        def mutate(project):
            (project / "RISKS.md").unlink()
            text = replaced(fixture_text("GATES.md"), "| open |", "| closed |")
            (project / "GATES.md").write_text(text, encoding="utf-8")
        backlog = self.build(mutate=mutate)
        self.assertIn("AC-002", self.origins(backlog))
        self.assertTrue(any("RISKS.md" in n and "missing" in n for n in backlog.notes), backlog.notes)
        self.assertTrue(any("GATES.md" in n and "validation error" in n for n in backlog.notes), backlog.notes)

    def test_undeclared_registers_are_skipped_silently(self):
        def mutate(project):
            text = "\n".join(l for l in fixture_text("PROJECT.md").splitlines()
                             if not l.startswith(("- Risk register", "- Gate register"))) + "\n"
            (project / "PROJECT.md").write_text(text, encoding="utf-8")
        backlog = self.build(mutate=mutate)
        self.assertEqual(backlog.notes, [])
        self.assertNotIn("G-002", self.origins(backlog))

    def test_render_markdown_table(self):
        out = pb.render(self.build())
        lines = out.splitlines()
        self.assertEqual(lines[0], "| Due | Days | Origin | Owner | What |")
        self.assertEqual(lines[1], "|---|---|---|---|---|")
        self.assertTrue(lines[2].startswith("| 2026-11-25 | 2 | AC-002 | Project manager | "), lines[2])
        self.assertTrue(lines[-1].startswith("| - | - | CR-003 |"), lines[-1])

    def test_render_escapes_pipes(self):
        item = pb.Item(None, None, "AC-009", "ada-l", "a | b")
        self.assertIn("a \\| b", pb.render(pb.Backlog((item,), [])))

    def test_render_empty(self):
        self.assertIn("No open items", pb.render(pb.Backlog((), [])))

    def test_render_notes_after_table(self):
        out = pb.render(pb.Backlog((), ["RISKS.md is missing"]))
        self.assertIn("Not read: RISKS.md is missing", out)


class BacklogCommandLine(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPTS / "pm_backlog.py"), *args], capture_output=True, text=True)

    def test_prints_the_view(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            result = self.run_script(str(project / "PROJECT.md"), "--today", "2026-11-23", "--owner", "ada-l")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("| 2026-11-20 | -3 | AC-003 | ada-l |", result.stdout)

    def test_horizon_and_several_owners(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            result = self.run_script(str(project / "PROJECT.md"), "--today", "2026-11-23", "--owner", "ada-l",
                                     "--owner", "bo-k", "--days", "3")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("AC-003", result.stdout)
            self.assertNotIn("R-001", result.stdout)

    def test_usage_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            self.assertEqual(self.run_script(str(Path(tmp) / "none.md")).returncode, 2)
            self.assertEqual(self.run_script(str(project / "PROJECT.md"), "--today", "tomorrow").returncode, 2)
            self.assertEqual(self.run_script(str(project / "PROJECT.md"), "--days", "-1").returncode, 2)
            self.assertEqual(self.run_script().returncode, 2)

    def test_validate_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok, bad = Path(tmp) / "ok.md", Path(tmp) / "bad.md"
            ok.write_text(ACTIONS, encoding="utf-8")
            bad.write_text(replaced(ACTIONS, "Status: open", "Status: wip"), encoding="utf-8")
            run = lambda *a: subprocess.run([sys.executable, str(SCRIPTS / "actions_register.py"), *a],
                                            capture_output=True, text=True).returncode
            self.assertEqual(run("validate", str(ok)), 0)
            self.assertEqual(run("validate", str(bad)), 1)
            self.assertEqual(run("validate", str(Path(tmp) / "none.md")), 2)
            self.assertEqual(run(), 2)


if __name__ == "__main__":
    unittest.main()
