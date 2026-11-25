"""Tests of the schedule and budget registers, the critical path, earned value and estimates."""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from _support import FIXTURES, REPO, SCRIPTS, fixture_text

import budget_register as br
import estimate as es
import schedule_cpm as cpm
import schedule_register as sr

SCHEDULE = fixture_text("SCHEDULE.md")
BUDGET = fixture_text("BUDGET.md")
ACTIVITIES_CSV = fixture_text("schedule-activities.csv")
TODAY = date(2026, 11, 23)
MON_FRI = ("mon", "tue", "wed", "thu", "fri")


def replaced(text: str, old: str, new: str) -> str:
    assert old in text, old
    return text.replace(old, new, 1)


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, text=True)


def summary_of(module, name: str, text: str | None) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        if text is not None:
            path.write_text(text, encoding="utf-8")
        return module.summary_line(path, TODAY, label=name)


def doc_example(format_file: str) -> str:
    text = (REPO / "shared" / "registers" / format_file).read_text(encoding="utf-8")
    return re.search(r"```markdown\n(.*?)```", text, re.S).group(1)


def plan(rows: list[str], baselines: str = "") -> str:
    head = ("# Schedule\n\nSource: register\n\n## Activities\n\n"
            "| ID | Activity | Duration | Predecessors | Start | Finish | Progress |\n"
            "|---|---|---|---|---|---|---|\n")
    return head + "".join(f"| {row} |\n" for row in rows) + baselines


NETWORK = ["A-001 | Start | 0 |  |  |  | 0",
           "A-002 | Design | 5 | A-001 |  |  | 0",
           "A-003 | Build | 10 | A-002 |  |  | 0",
           "A-004 | Docs | 3 | A-002 |  |  | 0",
           "A-005 | Test | 4 | A-003, A-004 |  |  | 0",
           "A-006 | Done | 0 | A-005 |  |  | 0"]
MONDAY = date(2026, 3, 2)


def schedule_of(rows: list[str], start: date = MONDAY, status: date | None = None,
                days_off: frozenset[date] = frozenset()) -> cpm.Schedule:
    register, errors = sr.parse(plan(rows))
    assert errors == [], errors
    return cpm.cpm(register.activities, cpm.WorkCalendar(MON_FRI, days_off), start, status)


class ErrorAssertions(unittest.TestCase):
    def assertError(self, errors: list[str], line: int, keyword: str) -> None:
        matching = [e for e in errors if e.startswith(f"line {line}:") and keyword in e]
        self.assertTrue(matching, f"no 'line {line}: …{keyword}…' in {errors}")


class ScheduleRegister(ErrorAssertions):
    def test_fixture_and_example_are_valid(self):
        self.assertEqual(sr.validate(SCHEDULE), [])
        self.assertEqual(sr.validate(doc_example("schedule.md")), [])

    def test_parse(self):
        register, _ = sr.parse(SCHEDULE)
        self.assertEqual(register.source, "register")
        self.assertEqual(len(register.activities), 10)
        links = register.activities[7].links
        self.assertEqual([(l.pred, l.kind, l.lag) for l in links],
                         [("A-005", "FS", 0), ("A-006", "FS", 0), ("A-007", "FF", 5)])
        self.assertEqual([b.id for b in register.baselines], ["B-01", "B-02"])
        self.assertEqual(register.baselines[1].change, "CR-002")

    def test_tool_source_needs_no_activities(self):
        text = "# Schedule\n\nSource: Plan\n\n" + "## Baseline B-01" + SCHEDULE.split("## Baseline B-01")[1]
        self.assertEqual(sr.validate(text), [])

    def test_register_source_needs_activities(self):
        text = "# Schedule\n\nSource: register\n"
        self.assertTrue(any("## Activities" in e for e in sr.validate(text)))

    def test_rejects_missing_title_and_source(self):
        errors = sr.validate(SCHEDULE.replace("# Schedule\n", "").replace("Source: register\n", ""))
        self.assertTrue(any("title" in e for e in errors), errors)
        self.assertTrue(any("Source" in e for e in errors), errors)

    def test_rejects_unknown_self_and_duplicate_predecessors(self):
        errors = sr.validate(plan(["A-001 | One | 1 | A-009 |  |  | 0", "A-002 | Two | 1 | A-002 |  |  | 0",
                                   "A-003 | Three | 1 | A-001, A-001 |  |  | 0"]))
        self.assertError(errors, 9, "unknown predecessor")
        self.assertError(errors, 10, "itself")
        self.assertError(errors, 11, "twice")

    def test_rejects_cycle(self):
        errors = sr.validate(plan(["A-001 | One | 1 |  |  |  | 0", "A-002 | Two | 1 | A-001, A-004 |  |  | 0",
                                   "A-003 | Three | 1 | A-002 |  |  | 0", "A-004 | Four | 1 | A-003 FF |  |  | 0"]))
        self.assertError(errors, 10, "cycle")
        self.assertTrue(any("A-002 → A-003 → A-004 → A-002" in e for e in errors), errors)
        self.assertEqual(sum("cycle" in e for e in errors), 1)

    def test_rejects_duplicate_ids_and_bad_cells(self):
        errors = sr.validate(plan(["A-001 | One | 1 |  |  |  | 0", "A-001 | Again | x | A-001 XX | 2026-13-01 |  | 120",
                                   "A-02 |  | 1 | A-001 FS+ |  |  | 0"]))
        self.assertError(errors, 10, "duplicate ID")
        self.assertError(errors, 10, "Duration")
        self.assertError(errors, 10, "predecessor 'A-001 XX'")
        self.assertError(errors, 10, "Start")
        self.assertError(errors, 10, "Progress")
        self.assertError(errors, 11, "ID 'A-02'")
        self.assertError(errors, 11, "Activity is empty")
        self.assertError(errors, 11, "predecessor 'A-001 FS+'")

    def test_rejects_unicode_digits(self):
        errors = sr.validate(plan(["A-00١ | One | ٢ |  |  |  | 0"]))
        self.assertError(errors, 9, "ID")
        self.assertError(errors, 9, "Duration")

    def test_rejects_finish_before_start_and_bad_milestone(self):
        errors = sr.validate(plan(["A-001 | One | 3 |  | 2026-03-05 | 2026-03-02 | 0",
                                   "A-002 | Gate | 0 | A-001 | 2026-03-09 | 2026-03-10 | 50"]))
        self.assertError(errors, 9, "before Start")
        self.assertError(errors, 10, "milestone")
        self.assertEqual(sum("milestone" in e for e in errors if e.startswith("line 10")), 2)

    def test_rejects_resource_column(self):
        text = replaced(SCHEDULE, "| Start | Finish | Progress |\n|---|---|---|---|---|---|---|",
                        "| Start | Finish | Progress | Owner |\n|---|---|---|---|---|---|---|---|")
        self.assertError(sr.validate(text), 7, "columns must be exactly")

    def test_rejects_contacts(self):
        self.assertError(sr.validate(replaced(SCHEDULE, "| Requirements |", "| Requirements a@b.io |")), 10, "email")

    def test_baseline_rules(self):
        text = replaced(SCHEDULE, "- Approved: 2026-11-04", "- Approved: 2025-12-01")
        text = replaced(text, "- Change: CR-002", "- Change: change 2")
        text = replaced(text, "| A-007 | Single sign-on | 2026-11-23 | 2026-12-11 |", "| A-007 | Single sign-on | 2026-11-23 |  |")
        text = replaced(text, "| A-009 | User acceptance | 2026-12-14", "| A-001 | User acceptance | 2026-12-14")
        errors = sr.validate(text)
        self.assertError(errors, 36, "before the approval of B-01")
        self.assertError(errors, 40, "CR-NNN")
        self.assertError(errors, 50, "Finish")
        self.assertError(errors, 52, "duplicate ID")

    def test_baseline_needs_entries_table_and_order(self):
        text = replaced(SCHEDULE, "- Approved by: steering committee\n- Change", "- Change")
        text = replaced(text, "## Baseline B-01 Initial plan", "## Baseline B-03 Initial plan")
        text += "\n## Baseline B-04 Empty\n\n- Approved: 2026-11-20\n- Approved by: sponsor\n- Owner: x\n"
        errors = sr.validate(text)
        self.assertError(errors, 36, "B-02 comes after B-03")
        self.assertError(errors, 36, "Approved by")
        self.assertTrue(any("B-04 has no table" in e for e in errors), errors)
        self.assertTrue(any("unknown entry 'Owner'" in e for e in errors), errors)

    def test_rejects_sections_out_of_order(self):
        text = "# Schedule\n\nSource: register\n\n## Baseline B-01" + SCHEDULE.split("## Baseline B-01")[1]
        text += "\n## Activities\n"
        errors = sr.validate(text)
        self.assertTrue(any("unexpected section" in e for e in errors), errors)

    def test_activities_csv(self):
        activities, errors = sr.parse_activities_csv(ACTIVITIES_CSV)
        self.assertEqual(errors, [])
        register, _ = sr.parse(SCHEDULE)
        self.assertEqual([(a.id, a.duration, a.links, a.start, a.finish, a.progress) for a in activities],
                         [(a.id, a.duration, a.links, a.start, a.finish, a.progress) for a in register.activities])

    def test_activities_csv_errors(self):
        self.assertError(sr.parse_activities_csv("id,activity,duration,owner\n")[1], 1, "header")
        errors = sr.parse_activities_csv("id,activity,duration,predecessors,start,finish,progress\n"
                                         "A-001,One,1,A-002,,,0\nA-002,Two,1,A-001,,,0\nA-003,Three,1\n")[1]
        self.assertTrue(any("cycle" in e for e in errors), errors)
        self.assertError(errors, 4, "7 fields")

    def test_summary(self):
        self.assertEqual(summary_of(sr, "SCHEDULE.md", SCHEDULE),
                         "Schedule register `SCHEDULE.md`: source register, 10 activities, "
                         "latest baseline B-02 approved 2026-11-04.")
        text = "# Schedule\n\nSource: Plan\n"
        self.assertEqual(summary_of(sr, "SCHEDULE.md", text),
                         "Schedule register `SCHEDULE.md`: source Plan, 0 activities, no baseline yet.")

    def test_summary_missing_and_invalid(self):
        self.assertEqual(summary_of(sr, "SCHEDULE.md", None), "Schedule register `SCHEDULE.md` is declared but "
                         "missing: run /pm-skills:schedule-check to create it.")
        self.assertEqual(summary_of(sr, "SCHEDULE.md", replaced(SCHEDULE, "| 85 |", "| 185 |")),
                         "Schedule register `SCHEDULE.md` has 1 validation error: "
                         "run /pm-skills:schedule-check to fix them.")


class WorkCalendar(unittest.TestCase):
    def test_counts_working_days_and_days_off(self):
        cal = cpm.WorkCalendar(MON_FRI, frozenset({date(2026, 3, 4)}))
        self.assertEqual(cal.add(date(2026, 3, 2), 3), date(2026, 3, 6))
        self.assertEqual(cal.between(date(2026, 3, 2), date(2026, 3, 9)), 4)
        self.assertEqual(cal.between(date(2026, 3, 9), date(2026, 3, 2)), -4)
        self.assertEqual(cal.next_working(date(2026, 3, 7)), date(2026, 3, 9))

    def test_from_capacity(self):
        import capacity_register as cr
        register, errors = cr.parse(fixture_text("CAPACITY.md"))
        self.assertEqual(errors, [])
        cal = cpm.calendar_from_capacity(register)
        self.assertEqual(cal.working_days, MON_FRI)
        self.assertIn(date(2026, 12, 8), cal.days_off)
        self.assertIn(date(2027, 1, 6), cal.days_off)
        self.assertNotIn(date(2026, 11, 27), cal.days_off)  # an event is a working day
        self.assertEqual(cal.next_working(date(2026, 12, 24)), date(2027, 1, 7))


class CriticalPath(unittest.TestCase):
    def dates(self, schedule: cpm.Schedule, activity: str) -> tuple:
        t = schedule.timing(activity)
        return t.early_start, t.early_finish, t.late_start, t.late_finish, t.total_float

    def test_forward_and_backward_pass(self):
        s = schedule_of(NETWORK)
        self.assertEqual(self.dates(s, "A-001"), (MONDAY, MONDAY, MONDAY, MONDAY, 0))
        self.assertEqual(self.dates(s, "A-002"), (MONDAY, date(2026, 3, 6), MONDAY, date(2026, 3, 6), 0))
        self.assertEqual(self.dates(s, "A-003"), (date(2026, 3, 9), date(2026, 3, 20), date(2026, 3, 9),
                                                  date(2026, 3, 20), 0))
        self.assertEqual(self.dates(s, "A-004"), (date(2026, 3, 9), date(2026, 3, 11), date(2026, 3, 18),
                                                  date(2026, 3, 20), 7))
        self.assertEqual(self.dates(s, "A-006")[:2], (date(2026, 3, 26), date(2026, 3, 26)))
        self.assertEqual(s.finish, date(2026, 3, 26))
        self.assertEqual(s.paths, (("A-001", "A-002", "A-003", "A-005", "A-006"),))

    def test_two_critical_paths(self):
        rows = list(NETWORK)
        rows[3] = "A-004 | Docs | 10 | A-002 |  |  | 0"
        self.assertEqual(schedule_of(rows).paths, (("A-001", "A-002", "A-003", "A-005", "A-006"),
                                                   ("A-001", "A-002", "A-004", "A-005", "A-006")))

    def test_lags_and_types(self):
        rows = ["A-001 | Dig | 10 |  |  |  | 0",
                "A-002 | Pour | 4 | A-001 SS+2 |  |  | 0",
                "A-003 | Cure | 3 | A-002 FF+1 |  |  | 0",
                "A-004 | Paint | 2 | A-003 FS-1 |  |  | 0",
                "A-005 | Fence | 2 | A-001 FS+2 |  |  | 0"]
        s = schedule_of(rows)
        self.assertEqual(s.timing("A-002").early_start, date(2026, 3, 4))
        self.assertEqual(s.timing("A-003").early_finish, date(2026, 3, 10))  # Pour ends 03-09, +1
        self.assertEqual(s.timing("A-004").early_start, date(2026, 3, 10))  # a lead of one day
        self.assertEqual(s.timing("A-005").early_start, date(2026, 3, 18))
        self.assertEqual(s.timing("A-005").early_finish, date(2026, 3, 19))
        self.assertEqual(s.paths, (("A-001", "A-005"),))
        self.assertEqual(s.timing("A-004").total_float, 6)

    def test_days_off_shift_dates(self):
        s = schedule_of(NETWORK, days_off=frozenset({date(2026, 3, 10)}))
        self.assertEqual(s.timing("A-003").early_finish, date(2026, 3, 23))
        self.assertEqual(s.finish, date(2026, 3, 27))

    def test_start_constraint(self):
        rows = list(NETWORK)
        rows[3] = "A-004 | Docs | 3 | A-002 | 2026-03-19 |  | 0"
        s = schedule_of(rows)
        self.assertEqual(s.timing("A-004").early_start, date(2026, 3, 19))
        self.assertEqual(s.finish, date(2026, 3, 27))
        self.assertEqual(s.paths, (("A-004", "A-005", "A-006"),))

    def test_deadline_gives_negative_float(self):
        rows = list(NETWORK)
        rows[5] = "A-006 | Done | 0 | A-005 |  | 2026-03-24 | 0"
        s = schedule_of(rows)
        self.assertEqual(s.timing("A-006").total_float, -2)
        self.assertEqual(s.timing("A-003").total_float, -2)
        self.assertEqual(s.timing("A-004").total_float, 5)
        self.assertEqual([t.id for t in s.missed], ["A-006"])

    def test_progress_and_status_date(self):
        rows = ["A-001 | Start | 0 |  | 2026-03-02 | 2026-03-02 | 100",
                "A-002 | Design | 5 | A-001 | 2026-03-03 | 2026-03-09 | 100",
                "A-003 | Build | 10 | A-002 | 2026-03-10 |  | 20",
                "A-004 | Docs | 3 | A-002 |  |  | 0",
                "A-005 | Test | 4 | A-003, A-004 |  |  | 0"]
        s = schedule_of(rows, status=date(2026, 3, 13))
        self.assertIsNone(s.timing("A-002").total_float)
        self.assertEqual(s.timing("A-002").early_finish, date(2026, 3, 9))
        self.assertEqual(s.timing("A-003").early_start, date(2026, 3, 10))
        self.assertEqual(s.timing("A-003").early_finish, date(2026, 3, 25))  # 8 days left from 03-16
        self.assertEqual(s.timing("A-004").early_start, date(2026, 3, 16))  # not before the status date
        self.assertEqual(s.timing("A-005").early_start, date(2026, 3, 26))
        self.assertEqual(s.paths, (("A-003", "A-005"),))

    def test_in_progress_without_status_date_keeps_duration(self):
        rows = ["A-001 | Build | 10 |  | 2026-03-02 |  | 50"]
        self.assertEqual(schedule_of(rows).timing("A-001").early_finish, date(2026, 3, 13))

    def test_fixture_with_capacity(self):
        import capacity_register as cr
        register, _ = sr.parse(SCHEDULE)
        cal = cpm.calendar_from_capacity(cr.parse(fixture_text("CAPACITY.md"))[0])
        s = cpm.cpm(register.activities, cal, date(2026, 1, 12), date(2026, 11, 20))
        self.assertTrue(s.paths)
        for path in s.paths:
            self.assertTrue(all(s.timing(a).critical for a in path))
        self.assertGreater(s.timing("A-007").early_start, s.timing("A-004").early_finish)

    def test_baseline_variance(self):
        baseline = ("\n## Baseline B-01 Plan\n\n- Approved: 2026-02-27\n- Approved by: sponsor\n\n"
                    "| ID | Activity | Start | Finish |\n|---|---|---|---|\n"
                    "| A-002 | Design | 2026-03-02 | 2026-03-06 |\n| A-003 | Build | 2026-03-09 | 2026-03-18 |\n"
                    "| A-005 | Test | 2026-03-19 | 2026-03-24 |\n| A-007 | Old | 2026-03-02 | 2026-03-03 |\n")
        register, errors = sr.parse(plan(NETWORK, baseline))
        self.assertEqual(errors, [])
        cal = cpm.WorkCalendar(MON_FRI, frozenset())
        s = cpm.cpm(register.activities, cal, MONDAY)
        v = cpm.variance(s, register.baselines[0], cal)
        rows = {r.id: (r.start_variance, r.finish_variance) for r in v.rows}
        self.assertEqual(rows, {"A-002": (0, 0), "A-003": (0, 2), "A-005": (2, 2)})
        self.assertEqual(v.added, ("A-001", "A-004", "A-006"))
        self.assertEqual(v.removed, ("A-007",))
        self.assertEqual((v.baseline_end, v.end, v.end_variance), (date(2026, 3, 24), date(2026, 3, 26), 2))


class ScheduleCli(unittest.TestCase):
    def files(self, tmp: str) -> tuple[str, str]:
        path = Path(tmp) / "SCHEDULE.md"
        path.write_text(SCHEDULE, encoding="utf-8")
        return str(path), str(FIXTURES / "CAPACITY.md")

    def test_validate(self):
        self.assertEqual(run("schedule_register.py", "validate", str(FIXTURES / "SCHEDULE.md")).returncode, 0)
        self.assertEqual(run("schedule_register.py", "validate").returncode, 2)

    def test_cpm_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            schedule, capacity = self.files(tmp)
            result = run("schedule_register.py", "cpm", schedule, "--capacity", capacity, "--status-date",
                         "2026-11-20", "--baseline", "latest")
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn("Calendar: working days mon, tue, wed, thu, fri", out)
        self.assertIn("2026-12-08", out)
        self.assertIn("Start: 2026-01-12", out)
        self.assertIn("Status date: 2026-11-20", out)
        self.assertIn("Critical path", out)
        self.assertIn("Baseline B-02", out)
        self.assertIn("End date", out)

    def test_cpm_from_csv_matches_register(self):
        with tempfile.TemporaryDirectory() as tmp:
            schedule, capacity = self.files(tmp)
            csv_path = str(FIXTURES / "schedule-activities.csv")
            a = run("schedule_register.py", "cpm", schedule, "--capacity", capacity, "--status-date", "2026-11-20")
            b = run("schedule_register.py", "cpm", schedule, "--capacity", capacity, "--status-date", "2026-11-20",
                    "--activities", csv_path)
        self.assertEqual((a.returncode, b.returncode), (0, 0), a.stderr + b.stderr)
        strip = lambda out: out.split("\n", 1)[1]  # the first line names the source of the activities
        self.assertEqual(strip(a.stdout), strip(b.stdout))

    def test_cpm_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            schedule, _ = self.files(tmp)
            self.assertEqual(run("schedule_register.py", "cpm", schedule, "--baseline", "B-09").returncode, 2)
            self.assertEqual(run("schedule_register.py", "cpm", schedule, "--start", "nope").returncode, 2)
            self.assertEqual(run("schedule_register.py", "cpm", str(Path(tmp) / "none.md")).returncode, 2)
            bad = Path(tmp) / "bad.md"
            bad.write_text(replaced(SCHEDULE, "| A-004 SS+130 |", "| A-008 |"), encoding="utf-8")
            result = run("schedule_register.py", "cpm", str(bad))
            self.assertEqual(result.returncode, 1)
            self.assertIn("cycle", result.stderr)
            tool = Path(tmp) / "tool.md"
            tool.write_text("# Schedule\n\nSource: Plan\n", encoding="utf-8")
            self.assertEqual(run("schedule_register.py", "cpm", str(tool), "--start", "2026-01-12").returncode, 1)


class BudgetRegister(ErrorAssertions):
    def test_fixture_and_example_are_valid(self):
        self.assertEqual(br.validate(BUDGET), [])
        self.assertEqual(br.validate(doc_example("budget.md")), [])

    def test_totals(self):
        register, _ = br.parse(BUDGET)
        self.assertEqual(register.currency, "EUR")
        totals = br.totals(register)
        self.assertEqual(totals.bac, Decimal("208100.00"))
        self.assertEqual(totals.contingency, Decimal("8400.00"))
        self.assertEqual(totals.management_reserve, Decimal("10000.00"))
        self.assertEqual(br.totals(register, until=date(2026, 10, 1)).bac, Decimal("200000.00"))

    def test_rate_in_force(self):
        register, _ = br.parse(BUDGET)
        self.assertEqual(br.rate_on(register, "developer", date(2026, 6, 30)).rate, Decimal("520"))
        self.assertEqual(br.rate_on(register, "Developer", date(2026, 7, 1)).rate, Decimal("540"))
        self.assertIsNone(br.rate_on(register, "developer", date(2026, 1, 1)))
        self.assertIsNone(br.rate_on(register, "architect", date(2026, 7, 1)))

    def test_rejects_preamble_errors(self):
        errors = br.validate(replaced(replaced(BUDGET, "Currency: EUR", "Currency: euro"),
                                      "Last reviewed: 2026-11-20", "Last reviewed: yesterday"))
        self.assertError(errors, 3, "ISO 4217")
        self.assertError(errors, 4, "Last reviewed")
        self.assertTrue(any("Currency" in e for e in br.validate(BUDGET.replace("Currency: EUR\n", ""))))

    def test_rejects_bad_lines(self):
        text = replaced(BUDGET, "| B-002 | Cloud hosting | expense | 14400.00 |", "| B-002 | Cloud hosting | travel | 14,400 |")
        text = replaced(text, "| B-003 | Managed message broker | expense | 0 | 2026-10-01 | 2026-12-18 |",
                        "| B-001 |  | expense | 1.234 | 2026-12-01 | 2026-10-18 |")
        errors = br.validate(text)
        self.assertError(errors, 11, "Kind")
        self.assertError(errors, 11, "Amount")
        self.assertError(errors, 12, "duplicate ID")
        self.assertError(errors, 12, "Line is empty")
        self.assertError(errors, 12, "Amount")
        self.assertError(errors, 12, "before From")

    def test_rejects_ids_out_of_order(self):
        self.assertError(br.validate(replaced(BUDGET, "| B-003 |", "| B-009 |")), 13, "ID order")

    def test_rejects_bad_rates(self):
        text = replaced(BUDGET, "| designer | 480 | day |", "| designer | 0 | week |")
        text = replaced(text, "| developer | 540 | day | 2026-07-01 |", "| developer | 540 | day | 2026-01-12 |")
        errors = br.validate(text)
        self.assertError(errors, 21, "Rate")
        self.assertError(errors, 21, "Unit")
        self.assertError(errors, 23, "same From")

    def test_rejects_bad_changes(self):
        text = replaced(BUDGET, "| 2026-09-18 | B-004 | -3600.00 | D-002 |", "| 2026-09-18 | B-004 | -13600.00 | D-002 |")
        text = replaced(text, "| 2026-09-18 | B-003 | +3600.00 | D-002 |", "| 2026-09-18 | B-007 | 0 | approved |")
        errors = br.validate(text)
        self.assertError(errors, 29, "below zero")
        self.assertError(errors, 30, "unknown line")
        self.assertError(errors, 30, "Amount")
        self.assertError(errors, 30, "CR-NNN or D-NNN")

    def test_rejects_name_column_and_contacts(self):
        text = replaced(BUDGET, "| Role | Rate | Unit | From |\n|---|---|---|---|",
                        "| Role | Name | Rate | Unit | From |\n|---|---|---|---|---|")
        self.assertError(br.validate(text), 18, "columns must be exactly")
        self.assertError(br.validate(replaced(BUDGET, "| tester |", "| tester +39 02 1234 5678 |")), 22, "phone")

    def test_optional_changes_and_section_order(self):
        self.assertEqual(br.validate(BUDGET.split("## Approved changes")[0]), [])
        errors = br.validate(replaced(BUDGET, "## Rates", "## Approved changes"))
        self.assertTrue(any("unexpected section" in e for e in errors), errors)

    def test_summary(self):
        self.assertEqual(summary_of(br, "BUDGET.md", BUDGET),
                         "Budget register `BUDGET.md`: budget 208100.00 EUR, reserves 18400.00 EUR "
                         "(contingency 8400.00, management reserve 10000.00), last reviewed 2026-11-20.")
        self.assertIn("never reviewed", summary_of(br, "BUDGET.md", BUDGET.replace("Last reviewed: 2026-11-20\n", "")))

    def test_summary_missing_and_invalid(self):
        self.assertEqual(summary_of(br, "BUDGET.md", None), "Budget register `BUDGET.md` is declared but missing: "
                         "run /pm-skills:budget-tracker to create it.")
        self.assertEqual(summary_of(br, "BUDGET.md", replaced(BUDGET, "| labor |", "| people |")),
                         "Budget register `BUDGET.md` has 1 validation error: run /pm-skills:budget-tracker to fix them.")


class EarnedValue(unittest.TestCase):
    def test_figures(self):
        r = br.earned_value(Decimal("1000"), Decimal("500"), Decimal("400"), Decimal("500"))
        self.assertEqual((r.cv, r.sv), (Decimal("-100"), Decimal("-100")))
        self.assertEqual((r.cpi, r.spi), (Decimal("0.8"), Decimal("0.8")))
        self.assertEqual(r.eac, Decimal("1250"))
        self.assertEqual(r.etc, Decimal("750"))
        self.assertEqual(r.vac, Decimal("-250"))
        self.assertEqual(r.eac_cpi_spi, Decimal("1437.5"))
        self.assertEqual(r.tcpi, Decimal("1.2"))

    def test_division_by_zero(self):
        r = br.earned_value(Decimal("1000"), Decimal("0"), Decimal("0"), Decimal("0"))
        self.assertIsNone(r.cpi)
        self.assertIsNone(r.spi)
        self.assertIsNone(r.eac)
        self.assertEqual(r.tcpi, Decimal("1"))
        self.assertIsNone(br.earned_value(Decimal("100"), Decimal("1"), Decimal("1"), Decimal("100")).tcpi)

    def test_cli_arguments(self):
        result = run("budget_register.py", "evm", str(FIXTURES / "BUDGET.md"), "--status-date", "2026-11-20",
                     "--pv", "150000", "--ev", "140000", "--ac", "160000", "--eac-cpi-spi")
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn("BAC = 208100.00 EUR", out)
        self.assertIn("CV = EV - AC = 140000.00 - 160000.00 = -20000.00", out)
        self.assertIn("CPI = EV / AC = 140000.00 / 160000.00 = 0.88", out)
        self.assertIn("SPI = EV / PV = 140000.00 / 150000.00 = 0.93", out)
        self.assertIn("EAC = BAC / CPI = BAC × AC / EV = 208100.00 × 160000.00 / 140000.00 = 237828.57", out)
        self.assertIn("EAC (CPI × SPI)", out)
        self.assertIn("TCPI = (BAC - EV) / (BAC - AC) = 68100.00 / 48100.00 = 1.42", out)
        self.assertIn("contingency 8400.00", out)

    def test_cli_data_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "evm.csv"
            data.write_text("date,pv,ev,ac\n2026-09-30,90000,85000,88000\n2026-10-31,120000,110000,118000\n"
                            "2026-11-30,150000,140000,160000\n", encoding="utf-8")
            result = run("budget_register.py", "evm", str(FIXTURES / "BUDGET.md"), "--status-date", "2026-11-20",
                         "--data", str(data))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("2026-10-31", result.stdout)
            self.assertNotIn("2026-11-30", result.stdout)
            self.assertIn("EV - AC = 110000.00 - 118000.00 = -8000.00", result.stdout)
            early = run("budget_register.py", "evm", str(FIXTURES / "BUDGET.md"), "--status-date", "2026-09-01",
                        "--data", str(data))
            self.assertEqual(early.returncode, 1)
            data.write_text("date,pv,ev,ac,owner\n", encoding="utf-8")
            self.assertEqual(run("budget_register.py", "evm", str(FIXTURES / "BUDGET.md"), "--status-date",
                                 "2026-11-20", "--data", str(data)).returncode, 1)

    def test_cli_errors(self):
        budget = str(FIXTURES / "BUDGET.md")
        self.assertEqual(run("budget_register.py", "evm", budget, "--status-date", "2026-11-20").returncode, 2)
        self.assertEqual(run("budget_register.py", "evm", budget, "--status-date", "2026-11-20", "--pv", "-1",
                             "--ev", "1", "--ac", "1").returncode, 2)
        self.assertEqual(run("budget_register.py", "validate", budget).returncode, 0)


class Estimates(unittest.TestCase):
    def test_pert(self):
        e = es.pert(Decimal("3"), Decimal("5"), Decimal("10"))
        self.assertEqual(e.mean.quantize(Decimal("0.01")), Decimal("5.50"))
        self.assertEqual(e.sd.quantize(Decimal("0.01")), Decimal("1.17"))

    def test_total(self):
        items = [es.Item("a", Decimal("3"), Decimal("5"), Decimal("10")),
                 es.Item("b", Decimal("2"), Decimal("4"), Decimal("8"))]
        total = es.total(items)
        self.assertEqual(total.mean.quantize(Decimal("0.01")), Decimal("9.83"))
        self.assertEqual(total.sd.quantize(Decimal("0.01")), Decimal("1.54"))
        self.assertEqual(es.percentile(total, 50).quantize(Decimal("0.01")), Decimal("9.83"))
        self.assertEqual(es.percentile(total, 85).quantize(Decimal("0.01")), Decimal("11.43"))

    def test_pert_cli(self):
        result = run("estimate.py", "pert", "--optimistic", "3", "--likely", "5", "--pessimistic", "10")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Mean = (O + 4M + P) / 6 = (3 + 4 × 5 + 10) / 6 = 5.50", result.stdout)
        self.assertIn("normal approximation", result.stdout)
        self.assertEqual(run("estimate.py", "pert", "--optimistic", "6", "--likely", "5",
                             "--pessimistic", "10").returncode, 1)

    def test_items_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            items = Path(tmp) / "items.csv"
            items.write_text("item,optimistic,likely,pessimistic\nLogin,3,5,10\nExport,2,4,8\n", encoding="utf-8")
            result = run("estimate.py", "pert", "--items", str(items))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Total mean: 9.83", result.stdout)
            self.assertIn("85%: 11.43", result.stdout)
            items.write_text("item,optimistic,likely,pessimistic\nLogin,3,5\nLogin,9,5,1\n", encoding="utf-8")
            result = run("estimate.py", "pert", "--items", str(items))
            self.assertEqual(result.returncode, 1)
            self.assertIn("line 2", result.stdout + result.stderr)
            self.assertIn("line 3", result.stdout + result.stderr)

    def test_cost_cli(self):
        budget = str(FIXTURES / "BUDGET.md")
        result = run("estimate.py", "cost", "--budget", budget, "--role", "developer", "--effort", "10",
                     "--unit", "day", "--date", "2026-11-20")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Cost = 10 day × 540.00 EUR = 5400.00 EUR", result.stdout)
        hours = run("estimate.py", "cost", "--budget", budget, "--role", "tester", "--effort", "2", "--unit", "day",
                    "--date", "2026-11-20", "--hours-per-day", "8")
        self.assertIn("= 880.00 EUR", hours.stdout)
        self.assertEqual(run("estimate.py", "cost", "--budget", budget, "--role", "tester", "--effort", "2",
                             "--unit", "day", "--date", "2026-11-20").returncode, 2)
        self.assertEqual(run("estimate.py", "cost", "--budget", budget, "--role", "architect", "--effort", "2",
                             "--unit", "day", "--date", "2026-11-20").returncode, 1)



NOT_UTF8 = b"\xff\xfe\x00bad \x80\x81\n"
HUGE_FIELD = "x" * 200000
TWENTY_DIGITS = "9" * 20
MAX_AMOUNT = "999999999999999"


class RobustInputs(ErrorAssertions):
    """Hostile or unusual inputs end with a message and exit 1 or 2, never a traceback."""

    def assertClean(self, result: subprocess.CompletedProcess, code: int) -> None:
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        self.assertTrue((result.stdout + result.stderr).strip())

    def test_files_that_are_not_utf8_are_an_io_error(self):
        budget = str(FIXTURES / "BUDGET.md")
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.bin"
            bad.write_bytes(NOT_UTF8)
            schedule = Path(tmp) / "SCHEDULE.md"
            schedule.write_text(SCHEDULE, encoding="utf-8")
            cases = [("estimate.py", "pert", "--items", str(bad)),
                     ("estimate.py", "cost", "--budget", str(bad), "--role", "developer", "--effort", "1",
                      "--unit", "day"),
                     ("budget_register.py", "validate", str(bad)),
                     ("budget_register.py", "evm", str(bad), "--status-date", "2026-11-20", "--pv", "1", "--ev",
                      "1", "--ac", "1"),
                     ("budget_register.py", "evm", budget, "--status-date", "2026-11-20", "--data", str(bad)),
                     ("schedule_register.py", "validate", str(bad)),
                     ("schedule_register.py", "cpm", str(bad)),
                     ("schedule_register.py", "cpm", str(schedule), "--activities", str(bad)),
                     ("schedule_register.py", "cpm", str(schedule), "--capacity", str(bad))]
            for script, *args in cases:
                with self.subTest(args=args):
                    self.assertClean(run(script, *args), 2)

    def test_amounts_with_too_many_digits_are_invalid_data(self):
        self.assertError(br.validate(replaced(BUDGET, "| 182000.00 |", f"| {TWENTY_DIGITS} |")), 10, "Amount")
        self.assertError(br.validate(replaced(BUDGET, "| 182000.00 |", "| 1000000000000000 |")), 10, "Amount")
        self.assertEqual(br.validate(replaced(BUDGET, "| 182000.00 |", f"| {MAX_AMOUNT}.99 |")), [])
        self.assertNotEqual(br.validate(replaced(BUDGET, "| -3600.00 |", f"| -{TWENTY_DIGITS} |")), [])
        self.assertNotEqual(br.validate(replaced(BUDGET, "| 520 |", f"| {TWENTY_DIGITS} |")), [])
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp) / "BUDGET.md"
            big.write_text(replaced(BUDGET, "| 182000.00 |", f"| {'9' * 40} |"), encoding="utf-8")
            self.assertClean(run("budget_register.py", "validate", str(big)), 1)
            self.assertIn("has 1 validation error:", br.summary_line(big, TODAY))

    def test_numbers_with_too_many_digits_are_refused_on_the_command_line(self):
        budget = str(FIXTURES / "BUDGET.md")
        cases = [("estimate.py", "pert", "--optimistic", "1", "--likely", "2", "--pessimistic", TWENTY_DIGITS),
                 ("estimate.py", "cost", "--budget", budget, "--role", "developer", "--effort", TWENTY_DIGITS,
                  "--unit", "day", "--date", "2026-11-20"),
                 ("estimate.py", "cost", "--budget", budget, "--role", "tester", "--effort", "1", "--unit",
                  "day", "--date", "2026-11-20", "--hours-per-day", TWENTY_DIGITS),
                 ("budget_register.py", "evm", budget, "--status-date", "2026-11-20", "--pv", TWENTY_DIGITS,
                  "--ev", "1", "--ac", "1"),
                 ("estimate.py", "pert", "--optimistic", "١", "--likely", "2", "--pessimistic", "3")]
        for script, *args in cases:
            with self.subTest(args=args):
                self.assertClean(run(script, *args), 2)

    def test_numbers_with_too_many_digits_in_csv_are_invalid_data(self):
        budget = str(FIXTURES / "BUDGET.md")
        with tempfile.TemporaryDirectory() as tmp:
            items = Path(tmp) / "items.csv"
            items.write_text(f"item,optimistic,likely,pessimistic\nLogin,1,2,{TWENTY_DIGITS}\n", encoding="utf-8")
            self.assertClean(run("estimate.py", "pert", "--items", str(items)), 1)
            data = Path(tmp) / "evm.csv"
            data.write_text(f"date,pv,ev,ac\n2026-09-30,{TWENTY_DIGITS},1,1\n", encoding="utf-8")
            self.assertClean(run("budget_register.py", "evm", budget, "--status-date", "2026-11-20",
                                 "--data", str(data)), 1)

    def test_extreme_but_valid_figures_are_shown(self):
        result = run("budget_register.py", "evm", str(FIXTURES / "BUDGET.md"), "--status-date", "2026-11-20",
                     "--pv", MAX_AMOUNT, "--ev", "0.01", "--ac", MAX_AMOUNT, "--eac-cpi-spi")
        self.assertClean(result, 0)
        result = run("estimate.py", "pert", "--optimistic", MAX_AMOUNT, "--likely", MAX_AMOUNT,
                     "--pessimistic", MAX_AMOUNT)
        self.assertClean(result, 0)

    def test_field_larger_than_the_csv_limit_is_a_data_error(self):
        budget = str(FIXTURES / "BUDGET.md")
        with tempfile.TemporaryDirectory() as tmp:
            items = Path(tmp) / "items.csv"
            items.write_text(f"item,optimistic,likely,pessimistic\n{HUGE_FIELD},1,2,3\n", encoding="utf-8")
            result = run("estimate.py", "pert", "--items", str(items))
            self.assertClean(result, 1)
            self.assertIn("line 2", result.stderr)
            data = Path(tmp) / "evm.csv"
            data.write_text(f"date,pv,ev,ac\n2026-09-30,{HUGE_FIELD},1,1\n", encoding="utf-8")
            result = run("budget_register.py", "evm", budget, "--status-date", "2026-11-20", "--data", str(data))
            self.assertClean(result, 1)
            self.assertIn("line 2", result.stderr)
            schedule = Path(tmp) / "SCHEDULE.md"
            schedule.write_text(SCHEDULE, encoding="utf-8")
            activities = Path(tmp) / "activities.csv"
            activities.write_text(ACTIVITIES_CSV.splitlines()[0] + f"\nA-001,{HUGE_FIELD},1,,,,0\n",
                                  encoding="utf-8")
            result = run("schedule_register.py", "cpm", str(schedule), "--activities", str(activities))
            self.assertClean(result, 1)
            self.assertIn("line 2", result.stderr)
        _, errors = sr.parse_activities_csv(ACTIVITIES_CSV.splitlines()[0] + f"\nA-001,{HUGE_FIELD},1,,,,0\n")
        self.assertError(errors, 2, "field")

    def test_dates_at_the_end_of_the_calendar_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SCHEDULE.md"
            path.write_text(plan(NETWORK), encoding="utf-8")
            self.assertClean(run("schedule_register.py", "cpm", str(path), "--start", "9999-12-31"), 2)
            self.assertClean(run("schedule_register.py", "cpm", str(path), "--start", "2026-03-02",
                                 "--status-date", "9999-12-31"), 2)
            path.write_text(plan(["A-001 | One | 5 |  | 9999-12-15 |  | 0"]), encoding="utf-8")
            self.assertClean(run("schedule_register.py", "cpm", str(path)), 1)

    def test_empty_baseline_is_invalid(self):
        baseline = ("\n## Baseline B-01 Empty\n\n- Approved: 2026-01-01\n- Approved by: sponsor\n\n"
                    "| ID | Activity | Start | Finish |\n|---|---|---|---|\n")
        self.assertTrue(any("baseline B-01 has no rows" in e for e in sr.validate(plan(NETWORK, baseline))),
                        sr.validate(plan(NETWORK, baseline)))

    def test_second_last_reviewed_line_is_rejected(self):
        text = replaced(BUDGET, "Last reviewed:", "Last reviewed: 2020-01-01\nLast reviewed:")
        errors = br.validate(text)
        self.assertTrue(any("Last reviewed" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
