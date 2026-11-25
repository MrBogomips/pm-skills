"""Tests of the flow snapshot validator, flow metrics, the Monte Carlo forecast and the DORA metrics."""
from __future__ import annotations

import random
import subprocess
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from _support import FIXTURES, SCRIPTS, fixture_text

import dora
import flow_data as fd
import flow_metrics as fm
import forecast as fc

SNAPSHOT = fixture_text("flow-snapshot.csv")
LATER = fixture_text("flow-snapshot-later.csv")
WORKFLOW = fd.Workflow.parse("In Progress,Review", "Done")
TODAY = date(2026, 11, 23)
MAPPING = ["--started", "In Progress,Review", "--finished", "Done"]


def items_of(text: str) -> dict[str, fd.Item]:
    transitions, errors = fd.parse(text)
    assert errors == [], errors
    return {i.key: i for i in fd.items(transitions)}


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, text=True)


def steady_csv(weeks: int, per_week: int, end: date) -> str:
    """Items finishing per_week per 7-day week, the last week ending on end."""
    rows = ["item,type,state,entered_at"]
    n = 0
    for w in range(weeks):
        day = date.fromordinal(end.toordinal() - 7 * w - 1)
        for _ in range(per_week):
            n += 1
            rows += [f"ACME-{n},story,In Progress,{date.fromordinal(day.toordinal() - 1)}",
                     f"ACME-{n},story,Done,{day}"]
    return "\n".join(rows) + "\n"


class Validation(unittest.TestCase):
    def assertError(self, text: str, line: int, keyword: str) -> None:
        errors = fd.validate(text)
        matching = [e for e in errors if e.startswith(f"line {line}:") and keyword in e]
        self.assertTrue(matching, f"no 'line {line}: ...{keyword}...' in {errors}")

    def test_fixtures_are_valid(self):
        self.assertEqual(fd.validate(SNAPSHOT), [])
        self.assertEqual(fd.validate(LATER), [])

    def test_extra_person_column_is_rejected(self):
        text = "item,type,state,entered_at,assignee\nACME-1,story,Done,2026-11-02,ada-l\n"
        self.assertError(text, 1, "header")

    def test_reordered_header_is_rejected(self):
        self.assertError("type,item,state,entered_at\n", 1, "header")

    def test_empty_file_is_rejected(self):
        self.assertTrue(fd.validate(""))

    def test_wrong_number_of_cells(self):
        self.assertError("item,type,state,entered_at\nACME-1,story,Done,2026-11-02,ada-l\n", 2, "4 cells")

    def test_empty_cell(self):
        self.assertError("item,type,state,entered_at\nACME-1,,Done,2026-11-02\n", 2, "type")

    def test_bad_timestamps(self):
        for bad in ("02/11/2026", "20261102", "2026-13-01", "2026-11-02T25:00"):
            self.assertError(f"item,type,state,entered_at\nACME-1,story,Done,{bad}\n", 2, "entered_at")

    def test_duplicate_row(self):
        text = "item,type,state,entered_at\nACME-1,story,Done,2026-11-02\nACME-1,story,Done,2026-11-02\n"
        self.assertError(text, 3, "duplicate")

    def test_transitions_out_of_time_order(self):
        text = "item,type,state,entered_at\nACME-1,story,Done,2026-11-05\nACME-1,story,In Progress,2026-11-02\n"
        self.assertError(text, 3, "before")

    def test_type_changes_within_an_item(self):
        text = "item,type,state,entered_at\nACME-1,story,In Progress,2026-11-02\nACME-1,bug,Done,2026-11-05\n"
        self.assertError(text, 3, "type")

    def test_timestamps_with_offset_become_utc(self):
        self.assertEqual(fd.parse_timestamp("2026-11-04T01:00:00+02:00"), datetime(2026, 11, 3, 23, 0))
        self.assertEqual(fd.parse_timestamp("2026-11-04T09:00:00Z"), datetime(2026, 11, 4, 9, 0))
        self.assertEqual(fd.parse_timestamp("2026-11-04"), datetime(2026, 11, 4))
        self.assertIsNone(fd.parse_timestamp("yesterday"))

    def test_validate_cli(self):
        self.assertEqual(run("flow_data.py", "validate", str(FIXTURES / "flow-snapshot.csv")).returncode, 0)
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.csv"
            bad.write_text("item,type,state,entered_at,assignee\n", encoding="utf-8")
            result = run("flow_data.py", "validate", str(bad))
            self.assertEqual(result.returncode, 1)
            self.assertIn("line 1:", result.stdout)
        self.assertEqual(run("flow_data.py", "validate", "/no/such/file.csv").returncode, 2)
        self.assertEqual(run("flow_data.py").returncode, 2)


class Helpers(unittest.TestCase):
    def test_nearest_rank_percentile(self):
        values = [14, 1, 3, 11, 3, 7]
        self.assertEqual(fd.percentile(values, 50), 3)
        self.assertEqual(fd.percentile(values, 85), 14)
        self.assertEqual(fd.percentile([5], 95), 5)
        self.assertEqual(fd.percentile([1, 2, 3, 4], 50), 2)
        with self.assertRaises(ValueError):
            fd.percentile([], 50)

    def test_workflow_parse(self):
        self.assertEqual(WORKFLOW.started, frozenset({"In Progress", "Review"}))
        with self.assertRaises(ValueError):
            fd.Workflow.parse("Done", "Done")
        with self.assertRaises(ValueError):
            fd.Workflow.parse("", "Done")

    def test_weeks_end_on_the_last_day_and_cover_whole_weeks(self):
        weeks = fd.weeks_ending(TODAY, date(2026, 10, 25))
        self.assertEqual(len(weeks), 4)
        self.assertEqual((weeks[0].start, weeks[-1].end), (date(2026, 10, 27), TODAY))
        self.assertEqual(fd.weeks_ending(TODAY, date(2026, 11, 20)), ())

    def test_today_from_file_name(self):
        self.assertEqual(fd.date_from_name(Path("flow/2026-12-07-flow-snapshot.csv")), date(2026, 12, 7))
        self.assertIsNone(fd.date_from_name(Path("flow-snapshot.csv")))


class Items(unittest.TestCase):
    def setUp(self):
        self.items = items_of(SNAPSHOT)

    def test_cycle_time_counts_calendar_days_inclusive(self):
        self.assertEqual(self.items["ACME-101"].cycle_time(WORKFLOW), 7)
        self.assertEqual(self.items["ACME-103"].cycle_time(WORKFLOW), 1)
        self.assertIsNone(self.items["ACME-107"].cycle_time(WORKFLOW))

    def test_reopened_item_keeps_its_first_finish_and_is_in_progress_again(self):
        item = self.items["ACME-106"]
        self.assertEqual(item.finished_on(WORKFLOW), date(2026, 10, 31))
        self.assertEqual(item.cycle_time(WORKFLOW), 3)
        self.assertTrue(item.in_progress_on(WORKFLOW, TODAY))
        self.assertTrue(item.reopened_on(WORKFLOW, TODAY))
        self.assertEqual(item.age_on(WORKFLOW, TODAY), 26)

    def test_item_moved_back_before_start_is_not_in_progress(self):
        self.assertFalse(self.items["ACME-110"].in_progress_on(WORKFLOW, TODAY))
        self.assertFalse(self.items["ACME-108"].in_progress_on(WORKFLOW, TODAY))

    def test_finish_without_a_started_state_has_no_cycle_time(self):
        item = items_of("item,type,state,entered_at\nACME-1,story,Done,2026-11-02\n")["ACME-1"]
        self.assertEqual(item.finished_on(WORKFLOW), date(2026, 11, 2))
        self.assertIsNone(item.cycle_time(WORKFLOW))


class Metrics(unittest.TestCase):
    def setUp(self):
        transitions, _ = fd.parse(SNAPSHOT)
        self.groups = fm.compute(fd.items(transitions), WORKFLOW, date(2026, 10, 27), TODAY, TODAY,
                                 fm.Sle(10, 85))
        self.by_label = {g.label: g for g in self.groups}

    def test_groups_total_then_types(self):
        self.assertEqual([g.label for g in self.groups], ["all", "bug", "story", "task"])

    def test_cycle_time_percentiles(self):
        total = self.by_label["all"]
        self.assertEqual(sorted(f.cycle_time for f in total.finished), [1, 3, 3, 7, 11, 14])
        self.assertEqual(total.cycle_percentiles, {50: 3, 85: 14, 95: 14})
        self.assertEqual(self.by_label["story"].cycle_percentiles, {50: 7, 85: 14, 95: 14})

    def test_weekly_throughput_includes_zero_weeks(self):
        self.assertEqual(self.by_label["all"].throughput, (2, 2, 0, 2))
        self.assertEqual(self.by_label["task"].throughput, (0, 0, 0, 1))

    def test_wip_now_and_ages(self):
        ages = {w.key: w.age for w in self.by_label["all"].wip}
        self.assertEqual(ages, {"ACME-106": 26, "ACME-107": 15, "ACME-109": 4})

    def test_sle(self):
        total = self.by_label["all"]
        self.assertEqual([w.key for w in total.wip if w.past_sle], ["ACME-106", "ACME-107"])
        self.assertEqual(total.within_sle, 4)

    def test_wip_average(self):
        text = "item,type,state,entered_at\nACME-1,story,In Progress,2026-11-17\nACME-1,story,Done,2026-11-19\n"
        transitions, _ = fd.parse(text)
        group = fm.compute(fd.items(transitions), WORKFLOW, date(2026, 11, 17), TODAY, TODAY, None)[0]
        self.assertAlmostEqual(group.wip_average, 2 / 7)

    def test_report_shows_the_working(self):
        text = fm.report(self.groups, WORKFLOW, date(2026, 10, 27), TODAY, TODAY, fm.Sle(14, 85))
        for expected in ("nearest-rank", "2026-11-10 to 2026-11-16: 0", "ACME-106", "reopened", "past the SLE"):
            self.assertIn(expected, text)

    def test_cli(self):
        result = run("flow_metrics.py", str(FIXTURES / "flow-snapshot.csv"), *MAPPING, "--from", "2026-10-27",
                     "--today", "2026-11-23", "--sle-days", "14")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("p85 14", result.stdout)

    def test_cli_aligns_the_window_to_whole_weeks(self):
        result = run("flow_metrics.py", str(FIXTURES / "flow-snapshot.csv"), *MAPPING, "--from", "2026-10-25",
                     "--today", "2026-11-23")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2026-10-27", result.stdout)

    def test_cli_errors(self):
        self.assertEqual(run("flow_metrics.py", str(FIXTURES / "flow-snapshot.csv"), "--started", "Done",
                             "--finished", "Done").returncode, 2)
        self.assertEqual(run("flow_metrics.py", str(FIXTURES / "flow-snapshot.csv"), *MAPPING, "--from",
                             "2026-11-20", "--today", "2026-11-23").returncode, 2)
        self.assertEqual(run("flow_metrics.py", "/no/such.csv", *MAPPING).returncode, 2)
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.csv"
            bad.write_text("item,type,state,entered_at,assignee\n", encoding="utf-8")
            self.assertEqual(run("flow_metrics.py", str(bad), *MAPPING).returncode, 1)

    def test_compare(self):
        result = run("flow_metrics.py", "compare", str(FIXTURES / "flow-snapshot.csv"),
                     str(FIXTURES / "flow-snapshot-later.csv"), *MAPPING, "--weeks", "4",
                     "--old-today", "2026-11-23", "--new-today", "2026-12-07")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2026-11-23", result.stdout)
        self.assertIn("2026-12-07", result.stdout)
        self.assertIn("WIP now", result.stdout)

    def test_compare_rows(self):
        old_t, _ = fd.parse(SNAPSHOT)
        new_t, _ = fd.parse(LATER)
        old = fm.compute(fd.items(old_t), WORKFLOW, date(2026, 10, 27), TODAY, TODAY, None)
        new = fm.compute(fd.items(new_t), WORKFLOW, date(2026, 11, 10), date(2026, 12, 7), date(2026, 12, 7), None)
        rows = {r[0]: r[1:] for r in fm.compare_rows(old[0], new[0])}
        self.assertEqual(rows["WIP now"], ("3", "1"))
        self.assertEqual(rows["Finished"], ("6", "5"))


class Forecast(unittest.TestCase):
    def test_constant_throughput_gives_exact_dates(self):
        weeks = fc.simulate_when((2, 2, 2, 2), 6, 100, random.Random(1))
        self.assertEqual(set(weeks), {3})
        counts = fc.simulate_how_many((2, 2, 2, 2), 5, 100, random.Random(1))
        self.assertEqual(set(counts), {10})

    def test_fixed_seed_is_reproducible(self):
        a = fc.simulate_when((2, 2, 0, 2), 10, 1000, random.Random(7))
        b = fc.simulate_when((2, 2, 0, 2), 10, 1000, random.Random(7))
        self.assertEqual(a, b)
        self.assertEqual(fc.when_percentiles(a), fc.when_percentiles(b))

    def test_fixed_seed_known_values(self):
        weeks = fc.simulate_when((2, 2, 0, 2), 4, 10000, random.Random(1))
        # analytic check: P(2 weeks) = 0.5625, P(<= 3) = 0.84375, P(<= 4) = 0.949
        self.assertEqual(fc.when_percentiles(weeks), {50: 2, 85: 4, 95: 5})
        counts = fc.simulate_how_many((2, 2, 0, 2), 4, 10000, random.Random(1))
        self.assertEqual(fc.how_many_percentiles(counts), {50: 6, 85: 4, 95: 4})

    def test_how_many_85_means_at_least_in_85_percent_of_runs(self):
        counts = tuple(range(1, 101))
        result = fc.how_many_percentiles(counts)
        self.assertEqual(result[85], 15)
        self.assertGreaterEqual(sum(1 for c in counts if c >= result[85]) / len(counts), 0.85)

    def test_zero_history_cannot_forecast(self):
        with self.assertRaises(ValueError):
            fc.simulate_when((0, 0, 0), 3, 10, random.Random(1))

    def test_history_from_snapshot(self):
        transitions, _ = fd.parse(SNAPSHOT)
        self.assertEqual(fc.history(fd.items(transitions), WORKFLOW, TODAY, 4, None).throughput, (2, 2, 0, 2))
        self.assertEqual(fc.history(fd.items(transitions), WORKFLOW, TODAY, 4, "story").throughput, (1, 1, 0, 1))

    def test_when_cli(self):
        args = ["when", str(FIXTURES / "flow-snapshot.csv"), "--items", "4", *MAPPING, "--weeks-history", "4",
                "--seed", "1", "--today", "2026-11-23"]
        first, second = run("forecast.py", *args), run("forecast.py", *args)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertIn("85%: 2026-12-21 (4 weeks)", first.stdout)
        self.assertIn("seed 1", first.stdout)

    def test_how_many_cli(self):
        result = run("forecast.py", "how-many", str(FIXTURES / "flow-snapshot.csv"), "--until", "2026-12-21",
                     *MAPPING, "--weeks-history", "4", "--seed", "1", "--today", "2026-11-23")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("85%: at least 4", result.stdout)

    def test_steady_history_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-11-23-flow-snapshot.csv"
            path.write_text(steady_csv(4, 2, TODAY), encoding="utf-8")
            result = run("forecast.py", "when", str(path), "--items", "6", *MAPPING, "--weeks-history", "4",
                         "--seed", "3")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("95%: 2026-12-14", result.stdout)

    def test_cli_errors(self):
        self.assertEqual(run("forecast.py", "when", str(FIXTURES / "flow-snapshot.csv"), "--items", "0",
                             *MAPPING).returncode, 2)
        self.assertEqual(run("forecast.py", "soon").returncode, 2)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "f.csv"
            path.write_text("item,type,state,entered_at\nACME-1,story,To Do,2026-11-02\n", encoding="utf-8")
            self.assertEqual(run("forecast.py", "when", str(path), "--items", "3", *MAPPING,
                                 "--today", "2026-11-23").returncode, 1)


class Dora(unittest.TestCase):
    def setUp(self):
        self.deployments, errors = dora.parse_deployments(fixture_text("dora-deployments.csv"))
        self.assertEqual(errors, [])
        self.incidents, errors = dora.parse_incidents(fixture_text("dora-incidents.csv"))
        self.assertEqual(errors, [])
        self.result = dora.compute(self.deployments, self.incidents, date(2026, 11, 1), date(2026, 11, 30))

    def test_deployment_frequency(self):
        self.assertEqual(self.result.deployments, 5)
        self.assertEqual(self.result.days, 30)

    def test_lead_time(self):
        self.assertEqual(self.result.lead_times, (4.0, 6.0, 18.0, 48.0))

    def test_change_failure_rate(self):
        self.assertEqual(self.result.failed, 1)

    def test_time_to_restore(self):
        self.assertEqual(self.result.restore_times, (2.0, 6.0))
        self.assertEqual(self.result.unresolved, 1)

    def test_invalid_inputs(self):
        _, errors = dora.parse_deployments("deployed_at,commit_at,failed,author\n")
        self.assertTrue(errors)
        _, errors = dora.parse_deployments("deployed_at,commit_at,failed\n2026-11-02T10:00:00,,maybe\n")
        self.assertTrue(any("failed" in e for e in errors))
        _, errors = dora.parse_deployments("deployed_at,commit_at,failed\n2026-11-02T10:00:00,2026-11-03,no\n")
        self.assertTrue(any("after" in e for e in errors))
        _, errors = dora.parse_incidents("opened_at,restored_at\n2026-11-02T10:00:00,2026-11-01T10:00:00\n")
        self.assertTrue(any("before" in e for e in errors))

    def test_cli(self):
        result = run("dora.py", "--deployments", str(FIXTURES / "dora-deployments.csv"), "--incidents",
                     str(FIXTURES / "dora-incidents.csv"), "--from", "2026-11-01", "--to", "2026-11-30")
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in ("5 deployments", "20.0%", "nearest-rank", "1 incident not restored"):
            self.assertIn(expected, result.stdout)

    def test_cli_without_incidents_or_commit_times(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "d.csv"
            path.write_text("deployed_at,commit_at,failed\n2026-11-02T10:00:00,,no\n", encoding="utf-8")
            result = run("dora.py", "--deployments", str(path), "--from", "2026-11-01", "--to", "2026-11-30")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("not available", result.stdout)

    def test_cli_errors(self):
        self.assertEqual(run("dora.py", "--deployments", "/no/such.csv", "--from", "2026-11-01", "--to",
                             "2026-11-30").returncode, 2)
        self.assertEqual(run("dora.py", "--deployments", str(FIXTURES / "dora-deployments.csv"), "--from",
                             "2026-11-30", "--to", "2026-11-01").returncode, 2)



def no_traceback(test: unittest.TestCase, result: subprocess.CompletedProcess) -> None:
    test.assertNotIn("Traceback", result.stderr + result.stdout)


class RobustInputs(unittest.TestCase):
    """Hostile or unusual inputs end with a message and exit 1 or 2, never a traceback."""

    def test_fractional_seconds_of_any_length_parse_the_same_on_every_python(self):
        self.assertEqual(fd.parse_timestamp("2026-01-05T10:00:00.5Z"), datetime(2026, 1, 5, 10, 0, 0, 500000))
        self.assertEqual(fd.parse_timestamp("2026-01-06T10:00:00.1234+02:00"),
                         datetime(2026, 1, 6, 8, 0, 0, 123400))
        self.assertEqual(fd.parse_timestamp("2026-01-06 10:00:00.12"), datetime(2026, 1, 6, 10, 0, 0, 120000))
        self.assertEqual(fd.parse_timestamp("2026-01-06T10:00"), datetime(2026, 1, 6, 10, 0))
        self.assertEqual(fd.parse_timestamp("2026-01-06"), datetime(2026, 1, 6))

    def test_timestamps_take_ascii_digits_only(self):
        for value in ("2026-01-0٥", "2026-01-05T10:0٥", "2026-01-05T25:00", "2026-01-05T10:00+24:00",
                      "0001-01-01T00:00+05:00", "2026-01-05T10:00:00.1234567"):
            with self.subTest(value=value):
                self.assertIsNone(fd.parse_timestamp(value))

    def test_utf8_bom_is_stripped(self):
        self.assertEqual(fd.validate("﻿" + SNAPSHOT), [])
        _, errors = dora.parse_deployments("﻿deployed_at,commit_at,failed\n2026-11-02T10:00:00,,no\n")
        self.assertEqual(errors, [])

    def test_field_larger_than_the_csv_limit_is_a_data_error(self):
        huge = "x" * 200000
        errors = fd.validate(f"item,type,state,entered_at\nACME-1,story,Done,2026-11-02\nACME-2,{huge},Done,"
                             "2026-11-02\n")
        self.assertTrue(errors and errors[0].startswith("line "), errors)
        _, errors = dora.parse_deployments(f"deployed_at,commit_at,failed\n{huge},,no\n")
        self.assertTrue(errors and errors[0].startswith("line "), errors)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "f.csv"
            path.write_text(f"item,type,state,entered_at\nACME-1,{huge},Done,2026-11-02\n", encoding="utf-8")
            result = run("flow_data.py", "validate", str(path))
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("line ", result.stdout)
            no_traceback(self, result)

    def test_how_many_refuses_more_than_max_weeks(self):
        result = run("forecast.py", "how-many", str(FIXTURES / "flow-snapshot.csv"), "--until", "9999-12-31",
                     *MAPPING, "--runs", "1", "--seed", "1", "--today", "2026-11-23")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn(str(fc.MAX_WEEKS), result.stderr)

    def test_huge_week_counts_and_far_dates_are_refused(self):
        snapshot = str(FIXTURES / "flow-snapshot.csv")
        cases = [("forecast.py", "when", snapshot, "--items", "4", *MAPPING, "--weeks-history", "99999999999",
                  "--seed", "1", "--today", "2026-11-23"),
                 ("flow_metrics.py", "compare", snapshot, str(FIXTURES / "flow-snapshot-later.csv"), *MAPPING,
                  "--weeks", "99999999999"),
                 ("forecast.py", "when", snapshot, "--items", "4", *MAPPING, "--seed", "1", "--today",
                  "2026-11-23", "--start", "9999-12-01"),
                 ("forecast.py", "when", snapshot, "--items", "4", *MAPPING, "--weeks-history", "1000",
                  "--seed", "1", "--today", "0001-01-10"),
                 ("flow_metrics.py", "compare", snapshot, str(FIXTURES / "flow-snapshot-later.csv"), *MAPPING,
                  "--weeks", "1000", "--old-today", "0001-01-10")]
        for script, *args in cases:
            with self.subTest(args=args):
                result = run(script, *args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertTrue(result.stderr.strip())
                no_traceback(self, result)

    def test_whole_number_options_take_ascii_digits_only(self):
        snapshot = str(FIXTURES / "flow-snapshot.csv")
        for bad in ("٥", "1_0", " 5", "5 ", "+5", "-1", "5.0", "99999999999999999999"):
            with self.subTest(value=bad):
                self.assertEqual(run("forecast.py", "when", snapshot, "--items", bad, *MAPPING,
                                     "--seed", "1", "--today", "2026-11-23").returncode, 2)
                self.assertEqual(run("forecast.py", "when", snapshot, "--items", "4", *MAPPING, "--runs", bad,
                                     "--seed", "1", "--today", "2026-11-23").returncode, 2)
                self.assertEqual(run("flow_metrics.py", snapshot, *MAPPING, "--sle-days", bad).returncode, 2)
                self.assertEqual(run("flow_metrics.py", snapshot, *MAPPING, "--sle-days", "5",
                                     "--sle-percent", bad).returncode, 2)


if __name__ == "__main__":
    unittest.main()
