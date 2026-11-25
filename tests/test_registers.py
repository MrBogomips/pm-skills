"""Tests of the project, tools, tailoring, risk, decision, stakeholder, capacity and change registers and of
document naming."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from _support import REPO, SCRIPTS, fixture_text

import capacity_register as cr
import changes_register as ch
import decisions_register as dr
import doc_naming as dn
import md_register as md
import project_register as pr
import risks_register as rr
import stakeholders_register as sr
import tailoring_register as tl
import tools_register as tr

PROJECT = fixture_text("PROJECT.md")
TOOLS = fixture_text("TOOLS.md")
TAILORING = fixture_text("TAILORING.md")
RISKS = fixture_text("RISKS.md")
DECISIONS = fixture_text("DECISIONS.md")
STAKEHOLDERS = fixture_text("STAKEHOLDERS.md")
CAPACITY = fixture_text("CAPACITY.md")
CHANGES = fixture_text("CHANGES.md")
TODAY = date(2026, 11, 23)
POINTS = {"risk-register": ("format", "scale", "rules", "terms"), "status-report": ("format", "steps", "terms"),
          "team-register": ()}


def replaced(text: str, old: str, new: str) -> str:
    assert old in text, old
    return text.replace(old, new, 1)


class ErrorAssertions(unittest.TestCase):
    def assertError(self, errors: list[str], line: int, keyword: str) -> None:
        matching = [e for e in errors if e.startswith(f"line {line}:") and keyword in e]
        self.assertTrue(matching, f"no 'line {line}: …{keyword}…' in {errors}")


class CountOf(unittest.TestCase):
    def test_singular_for_one(self):
        self.assertEqual(md.count_of(1, "validation error"), "1 validation error")

    def test_plural_otherwise(self):
        self.assertEqual(md.count_of(0, "validation error"), "0 validation errors")
        self.assertEqual(md.count_of(2, "validation error"), "2 validation errors")

    def test_irregular_plural(self):
        self.assertEqual(md.count_of(3, "entry", "entries"), "3 entries")


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

    def test_rejects_shared_file_through_normalized_paths(self):
        self.assertError(pr.validate(replaced(PROJECT, "`DECISIONS.md`", "`./RISKS.md`")), 34, "same file")

    def test_rejects_unicode_digits_without_crashing(self):
        self.assertError(pr.validate(replaced(PROJECT, "- Sprint length: 2", "- Sprint length: ²")), 19, "Sprint length")

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

    def test_accepts_versioned_coded_source_not_as_phone(self):
        text = replaced(DECISIONS, "`meeting-minutes/2026-09-18-meeting-minutes-steering.md`", "`ACME-MM-012-1.0.0.md`")
        self.assertEqual(dr.validate(text), [])

    def test_rejects_one_sided_supersession(self):
        self.assertError(dr.validate(replaced(DECISIONS, "- Supersedes: D-001\n", "")), 11, "Supersedes: D-001")

    def test_rejects_superseded_without_successor(self):
        errors = dr.validate(replaced(replaced(DECISIONS, "- Superseded by: D-002\n", ""), "- Supersedes: D-001\n", ""))
        self.assertError(errors, 3, "Superseded by")

    def test_rejects_out_of_order_and_bad_status(self):
        errors = dr.validate(replaced(replaced(DECISIONS, "## D-002", "## D-000"), "Status: accepted", "Status: open"))
        self.assertError(errors, 13, "ID order")
        self.assertError(errors, 16, "Status")


def summary_of(module, name: str, text: str | None, today: date = TODAY) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        if text is not None:
            path.write_text(text, encoding="utf-8")
        return module.summary_line(path, today)


class StakeholderRegister(ErrorAssertions):
    def test_fixture_is_valid(self):
        register, errors = sr.parse(STAKEHOLDERS)
        self.assertEqual(errors, [])
        self.assertEqual(register.last_reviewed, date(2026, 11, 10))
        self.assertEqual([s.id for s in register.stakeholders], ["S-001", "S-002", "S-003", "S-004"])
        self.assertTrue(register.stakeholders[1].below_desired)
        self.assertFalse(register.stakeholders[2].below_desired)

    def test_accepts_organization_and_name(self):
        self.assertEqual(sr.validate(replaced(STAKEHOLDERS, "| Security office | Acme Corp |  |",
                                              "| Security office | Acme Corp | Dee R. |")), [])

    def test_rejects_bad_id_and_duplicate(self):
        errors = sr.validate(replaced(replaced(STAKEHOLDERS, "| S-002 |", "| S-001 |"), "| S-004 |", "| SH-4 |"))
        self.assertError(errors, 8, "duplicate ID")
        self.assertError(errors, 10, "ID")

    def test_rejects_empty_stakeholder(self):
        self.assertError(sr.validate(replaced(STAKEHOLDERS, "| Sponsor |", "|  |")), 7, "Stakeholder is empty")

    def test_rejects_bad_levels(self):
        errors = sr.validate(replaced(replaced(STAKEHOLDERS, "| high | low |", "| huge | 3 |"),
                                      "| neutral | neutral |", "| hostile | neutral |"))
        self.assertError(errors, 8, "Interest")
        self.assertError(errors, 8, "Influence")
        self.assertError(errors, 9, "Current")

    def test_rejects_bad_status_and_review(self):
        errors = sr.validate(replaced(replaced(STAKEHOLDERS, "| inactive |", "| gone |"), "2027-01-15", "soon"))
        self.assertError(errors, 10, "Status")
        self.assertError(errors, 9, "Review")

    def test_gap_needs_approach(self):
        text = replaced(STAKEHOLDERS, "| Beta programme and release notes inside the portal |", "|  |")
        self.assertError(sr.validate(text), 8, "needs Approach")

    def test_active_needs_owner_and_review(self):
        errors = sr.validate(replaced(STAKEHOLDERS, "| ada-l | active | 2027-01-15 |", "|  | active |  |"))
        self.assertError(errors, 9, "needs Owner")
        self.assertError(errors, 9, "needs Review")

    def test_rejects_contacts(self):
        errors = sr.validate(replaced(replaced(STAKEHOLDERS, "| Security office | Acme Corp |  |",
                                               "| Security office | Acme Corp | +39 333 123 4567 |"),
                                      "| Project manager |", "| pm@acme.example |"))
        self.assertError(errors, 7, "email")
        self.assertError(errors, 9, "phone")

    def test_rejects_free_text_and_bad_header(self):
        errors = sr.validate(replaced(replaced(STAKEHOLDERS, "| Approach |", "| Notes |"), "Last reviewed",
                                      "Some notes\nLast reviewed"))
        self.assertError(errors, 3, "unexpected content")
        self.assertError(errors, 6, "columns")

    def test_rejects_missing_title_and_table(self):
        errors = sr.validate("Last reviewed: 2026-11-10\n")
        self.assertTrue(any("missing title" in e for e in errors), errors)
        self.assertTrue(any("missing the stakeholders table" in e for e in errors), errors)

    def test_summary(self):
        self.assertEqual(summary_of(sr, "STAKEHOLDERS.md", STAKEHOLDERS),
                         "Stakeholder register `STAKEHOLDERS.md`: 3 active, 2 below their desired engagement, "
                         "1 past their review date: run /pm-skills:stakeholder-register to review them.")
        self.assertEqual(summary_of(sr, "STAKEHOLDERS.md", STAKEHOLDERS, date(2026, 11, 1)),
                         "Stakeholder register `STAKEHOLDERS.md`: 3 active, 2 below their desired engagement.")

    def test_summary_missing_and_invalid(self):
        self.assertEqual(summary_of(sr, "STAKEHOLDERS.md", None), "Stakeholder register `STAKEHOLDERS.md` is declared "
                         "but missing: run /pm-skills:stakeholder-register to create it.")
        self.assertEqual(summary_of(sr, "STAKEHOLDERS.md", replaced(STAKEHOLDERS, "| active |", "| on |")),
                         "Stakeholder register `STAKEHOLDERS.md` has 1 validation error: "
                         "run /pm-skills:stakeholder-register to fix them.")


class CapacityRegister(ErrorAssertions):
    def test_fixture_is_valid(self):
        register, errors = cr.parse(CAPACITY)
        self.assertEqual(errors, [])
        self.assertEqual(register.working_days, ("mon", "tue", "wed", "thu", "fri"))
        self.assertEqual(len(register.calendar), 3)
        self.assertEqual([a.member for a in register.allocations if a.base], ["ada-l", "bo-k", "bo-k", "cy-t"])
        self.assertEqual(register.allocations[4].percent, 0)

    def test_working_days_default_and_custom(self):
        register, errors = cr.parse(replaced(CAPACITY, "Working days: mon, tue, wed, thu, fri\n\n", ""))
        self.assertEqual((errors, register.working_days), ([], cr.DEFAULT_WORKING_DAYS))
        register, errors = cr.parse(replaced(CAPACITY, "mon, tue, wed, thu, fri", "sun, mon, tue, wed"))
        self.assertEqual((errors, register.working_days), ([], ("sun", "mon", "tue", "wed")))

    def test_rejects_bad_working_days(self):
        self.assertError(cr.validate(replaced(CAPACITY, "thu, fri", "thu, friday")), 3, "friday")
        self.assertError(cr.validate(replaced(CAPACITY, "thu, fri", "thu, mon")), 3, "twice")

    def test_rejects_bad_calendar_rows(self):
        errors = cr.validate(replaced(replaced(replaced(CAPACITY, "| holiday |", "| vacation |"),
                                               "| 2026-12-24 | 2027-01-06 |", "| 2026-12-24 | 2026-12-20 |"),
                                      "| Public holiday |", "|  |"))
        self.assertError(errors, 9, "Kind")
        self.assertError(errors, 9, "Description is empty")
        self.assertError(errors, 10, "before From")

    def test_rejects_bad_allocation_rows(self):
        errors = cr.validate(replaced(replaced(replaced(CAPACITY, "| ada-l | 2026-01-12 |  | 100 |",
                                                        "| Ada L | 2026-01-12 |  | 100% |"),
                                               "| 50 |\n| bo-k", "| ½ |\n| bo-k"),
                                      "| 2026-12-01 | 2026-12-05 |", "| 2026-12-01 | 2026-11-05 |"))
        self.assertError(errors, 17, "Member")
        self.assertError(errors, 17, "Allocation")
        self.assertError(errors, 18, "Allocation")
        self.assertError(errors, 21, "before From")

    def test_rejects_allocation_above_100(self):
        self.assertError(cr.validate(replaced(CAPACITY, "| 80 |", "| 101 |")), 19, "0 to 100")

    def test_rejects_overlapping_periods(self):
        text = CAPACITY + "| ada-l | 2026-12-05 | 2026-12-09 | 50 |\n"
        self.assertError(cr.validate(text), 23, "overlaps")

    def test_accepts_adjacent_periods_and_other_members(self):
        text = CAPACITY + "| ada-l | 2026-12-06 | 2026-12-09 | 50 |\n| bo-k | 2026-12-01 | 2026-12-05 | 0 |\n"
        self.assertEqual(cr.validate(text), [])

    def test_rejects_base_rows_with_same_from(self):
        self.assertError(cr.validate(replaced(CAPACITY, "| bo-k | 2026-09-01 |", "| bo-k | 2026-02-01 |")), 19,
                         "same From")

    def test_rejects_sections_out_of_order_and_free_text(self):
        text = replaced(replaced(CAPACITY, "## Calendar", "## Allocation"), "| 2026-12-08 |", "Note\n| 2026-12-08 |")
        errors = cr.validate(text)
        self.assertTrue(any("unexpected section" in e or "missing section" in e for e in errors), errors)

    def test_rejects_free_text_and_contacts(self):
        errors = cr.validate(replaced(replaced(CAPACITY, "## Allocation", "Ask HR\n\n## Allocation"),
                                      "| Public holiday |", "| Call hr@acme.example |"))
        self.assertError(errors, 9, "email")
        self.assertError(errors, 13, "unexpected content")

    def test_rejects_missing_sections(self):
        errors = cr.validate("# Capacity\n")
        self.assertTrue(any("missing section '## Calendar'" in e for e in errors), errors)
        self.assertTrue(any("missing section '## Allocation'" in e for e in errors), errors)

    def test_summary(self):
        self.assertEqual(summary_of(cr, "CAPACITY.md", CAPACITY),
                         "Capacity register `CAPACITY.md`: 3 members with a base allocation, 2 periods starting in "
                         "the next 14 days, next day off 2026-12-08.")
        self.assertEqual(summary_of(cr, "CAPACITY.md", CAPACITY, date(2026, 12, 25)),
                         "Capacity register `CAPACITY.md`: 3 members with a base allocation, 0 periods starting in "
                         "the next 14 days, next day off 2026-12-25.")
        self.assertEqual(summary_of(cr, "CAPACITY.md", CAPACITY, date(2027, 2, 1)),
                         "Capacity register `CAPACITY.md`: 3 members with a base allocation, 0 periods starting in "
                         "the next 14 days, no day off ahead.")

    def test_summary_missing_and_invalid(self):
        self.assertEqual(summary_of(cr, "CAPACITY.md", None), "Capacity register `CAPACITY.md` is declared but "
                         "missing: run /pm-skills:capacity-register to create it.")
        self.assertEqual(summary_of(cr, "CAPACITY.md", replaced(CAPACITY, "| 80 |", "| 800 |")),
                         "Capacity register `CAPACITY.md` has 1 validation error: "
                         "run /pm-skills:capacity-register to fix them.")


SCENARIO_CAPACITY = """# Capacity

## Calendar

| From | To | Kind | Description |
|---|---|---|---|
| 2026-12-08 |  | holiday | Public holiday |
| 2026-12-24 | 2026-12-31 | closure | Winter closure |
| 2026-12-11 |  | event | All-hands |

## Allocation

| Member | From | To | Allocation |
|---|---|---|---|
| ada-l | 2026-01-12 |  | 100 |
| bo-k | 2026-02-01 |  | 50 |
| cy-t | 2026-09-01 |  | 100 |
| cy-t | 2026-12-14 | 2026-12-15 | 0 |
"""


class CapacityAvailable(unittest.TestCase):
    def result(self, text: str, start: date, end: date, member: str | None = None) -> cr.Availability:
        register, errors = cr.parse(text)
        self.assertEqual(errors, [])
        return cr.available(register, start, end, member)

    def test_scenario_team_and_member(self):
        result = self.result(SCENARIO_CAPACITY, date(2026, 12, 7), date(2026, 12, 18))
        self.assertEqual((result.working_days, result.counted_days), (10, 9))
        self.assertEqual([d for d, _ in result.days_off], [date(2026, 12, 8)])
        self.assertEqual([d for d, _ in result.events], [date(2026, 12, 11)])
        per_member = {m.member: cr.person_days(m.hundredths) for m in result.members}
        self.assertEqual(per_member, {"ada-l": "9", "bo-k": "4.5", "cy-t": "7"})
        self.assertEqual(cr.person_days(result.hundredths), "20.5")
        bo = self.result(SCENARIO_CAPACITY, date(2026, 12, 7), date(2026, 12, 18), "bo-k")
        self.assertEqual([m.member for m in bo.members], ["bo-k"])

    def test_fixture_periods_and_latest_base(self):
        result = self.result(CAPACITY, date(2026, 12, 7), date(2026, 12, 18))
        per_member = {m.member: cr.person_days(m.hundredths) for m in result.members}
        self.assertEqual(per_member, {"ada-l": "9", "bo-k": "7.2", "cy-t": "7"})
        cy = next(m for m in result.members if m.member == "cy-t")
        self.assertEqual([(s.start, s.end, s.days, s.percent) for s in cy.segments],
                         [(date(2026, 12, 7), date(2026, 12, 11), 4, 50),
                          (date(2026, 12, 14), date(2026, 12, 18), 5, 100)])
        self.assertEqual(cr.person_days(result.hundredths), "23.2")

    def test_event_on_a_day_off_is_not_listed_as_counted(self):
        text = replaced(CAPACITY, "| 2026-12-08 |  | holiday | Public holiday |",
                        "| 2026-12-08 |  | holiday | Public holiday |\n| 2026-12-08 |  | event | Office party |")
        result = self.result(text, date(2026, 12, 7), date(2026, 12, 9))
        self.assertEqual([d for d, _ in result.days_off], [date(2026, 12, 8)])
        self.assertEqual(result.events, ())

    def test_no_row_means_zero_and_custom_working_days(self):
        text = replaced(CAPACITY, "Working days: mon, tue, wed, thu, fri", "Working days: mon, tue, wed")
        result = self.result(text, date(2026, 1, 5), date(2026, 1, 18))
        self.assertEqual(result.working_days, 6)
        per_member = {m.member: m.hundredths for m in result.members}
        self.assertEqual(per_member, {"ada-l": 300, "bo-k": 0, "cy-t": 0})

    def test_closure_spanning_the_period(self):
        result = self.result(CAPACITY, date(2026, 12, 28), date(2026, 12, 31))
        self.assertEqual((result.working_days, result.counted_days, result.hundredths), (4, 0, 0))

    def test_person_days_format(self):
        self.assertEqual([cr.person_days(v) for v in (0, 450, 720, 705, 1000)], ["0", "4.5", "7.2", "7.05", "10"])

    def run_cli(self, text: str, *args: str) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CAPACITY.md"
            path.write_text(text, encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPTS / "capacity_register.py"), "available", str(path),
                                   *args], capture_output=True, text=True)

    def test_cli_shows_the_working(self):
        result = self.run_cli(SCENARIO_CAPACITY, "--from", "2026-12-07", "--to", "2026-12-18")
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout
        self.assertIn("Working days (mon, tue, wed, thu, fri): 10", out)
        self.assertIn("2026-12-08 holiday (Public holiday)", out)
        self.assertIn("Events, counted as working days: 2026-12-11 event (All-hands)", out)
        self.assertIn("  2026-12-14 to 2026-12-15: 2 days at 0% = 0", out)
        self.assertIn("  person-days: 4.5", out)
        self.assertTrue(out.rstrip().endswith("Total: 20.5 person-days"), out)

    def test_cli_one_member(self):
        result = self.run_cli(SCENARIO_CAPACITY, "--from", "2026-12-07", "--to", "2026-12-18", "--member", "bo-k")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("ada-l", result.stdout)
        self.assertIn("Total: 4.5 person-days", result.stdout)

    def test_cli_errors(self):
        dates = ("--from", "2026-12-07", "--to", "2026-12-18")
        self.assertEqual(self.run_cli(SCENARIO_CAPACITY, "--from", "2026-12-18", "--to", "2026-12-07").returncode, 2)
        self.assertEqual(self.run_cli(SCENARIO_CAPACITY, "--from", "7/12/2026", "--to", "2026-12-18").returncode, 2)
        self.assertEqual(self.run_cli(SCENARIO_CAPACITY, *dates, "--member", "di-r").returncode, 2)
        invalid = self.run_cli(replaced(SCENARIO_CAPACITY, "| 50 |", "| 500 |"), *dates)
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("Allocation", invalid.stderr)


class ChangeLog(ErrorAssertions):
    def test_fixture_is_valid(self):
        changes, errors = ch.parse(CHANGES)
        self.assertEqual(errors, [])
        self.assertEqual([c.id for c in changes], ["CR-001", "CR-002", "CR-003", "CR-004"])
        self.assertEqual(changes[1].fields["Status"], "approved")
        self.assertEqual(changes[1].decided_on, date(2026, 11, 4))

    def test_empty_log_is_valid(self):
        self.assertEqual(ch.validate("# Changes\n"), [])

    def test_rejects_missing_required_key(self):
        self.assertError(ch.validate(replaced(CHANGES, "- Reason: Asked for by end users in the beta feedback.\n",
                                              "")), 34, "needs 'Reason'")

    def test_assessed_needs_impacts(self):
        self.assertError(ch.validate(replaced(CHANGES, "- Cost impact: 5 person-days\n", "")), 42,
                         "needs 'Cost impact'")

    def test_withdrawn_may_lack_impacts(self):
        text = replaced(CHANGES, "- Status: assessed", "- Status: withdrawn")
        text = replaced(text, "- Cost impact: 5 person-days\n", "")
        self.assertEqual(ch.validate(text), [])

    def test_decided_needs_decision_keys(self):
        errors = ch.validate(replaced(replaced(CHANGES, "- Decided by: steering committee\n", ""),
                                      "- Decided on: 2026-11-04\n", ""))
        self.assertError(errors, 18, "needs 'Decided by'")
        self.assertError(errors, 18, "needs 'Decided on'")

    def test_undecided_must_not_have_decision_keys(self):
        text = replaced(CHANGES, "- Reason: Asked for", "- Decided by: Product owner\n- Reason: Asked for")
        self.assertError(ch.validate(text), 40, "only")

    def test_implemented_on_rules(self):
        self.assertError(ch.validate(replaced(CHANGES, "- Implemented on: 2026-10-02\n", "")), 3,
                         "needs 'Implemented on'")
        text = replaced(CHANGES, "- Source: `meeting", "- Implemented on: 2026-11-20\n- Source: `meeting")
        self.assertError(ch.validate(text), 32, "only")

    def test_rejects_dates_out_of_order(self):
        errors = ch.validate(replaced(replaced(CHANGES, "Decided on: 2026-09-10", "Decided on: 2026-08-10"),
                                      "Implemented on: 2026-10-02", "Implemented on: 2026-08-01"))
        self.assertError(errors, 15, "before Raised")
        self.assertError(errors, 16, "before Decided on")

    def test_rejects_bad_date_status_and_decision(self):
        errors = ch.validate(replaced(replaced(replaced(CHANGES, "Raised: 2026-11-12", "Raised: 12/11/2026"),
                                               "Status: assessed", "Status: parked"),
                                      "- Source: `meeting", "- Decision: decision 3\n- Source: `meeting"))
        self.assertError(errors, 37, "Raised")
        self.assertError(errors, 32, "D-NNN")
        self.assertError(errors, 47, "Status")

    def test_accepts_decision_reference(self):
        text = replaced(CHANGES, "- Source: `meeting", "- Decision: D-002\n- Source: `meeting")
        self.assertEqual(ch.validate(text), [])

    def test_rejects_out_of_order_duplicate_and_bad_heading(self):
        errors = ch.validate(replaced(replaced(replaced(CHANGES, "## CR-003", "## CR-001"), "## CR-004", "## CR-0004"),
                                      "## CR-002 Single", "## Single"))
        self.assertError(errors, 18, "heading")
        self.assertError(errors, 34, "duplicate ID")

    def test_rejects_decreasing_ids(self):
        self.assertError(ch.validate(replaced(CHANGES, "## CR-003", "## CR-005")), 42, "ID order")

    def test_rejects_same_number_with_other_padding(self):
        self.assertError(ch.validate(replaced(CHANGES, "## CR-004", "## CR-0002")), 42, "duplicate ID")

    def test_rejects_unknown_duplicate_empty_key_and_free_text(self):
        text = replaced(CHANGES, "- Reason: Asked for", "- Notes: x\n- Status: proposed\n- Source:\nfree text\n"
                                                         "- Reason: Asked for")
        errors = ch.validate(text)
        self.assertError(errors, 40, "unknown key")
        self.assertError(errors, 41, "already on line 38")
        self.assertError(errors, 42, "empty")
        self.assertError(errors, 43, "unexpected content")

    def test_rejects_contacts(self):
        errors = ch.validate(replaced(replaced(CHANGES, "Requested by: Finance lead", "Requested by: fin@acme.example"),
                                      "Requested by: Support lead", "Requested by: Support +39 02 1234 5678"))
        self.assertError(errors, 6, "email")
        self.assertError(errors, 45, "phone")

    def test_summary(self):
        self.assertEqual(summary_of(ch, "CHANGES.md", CHANGES),
                         "Change log `CHANGES.md`: 2 open (1 proposed, 1 assessed), 2 decided, "
                         "latest decision CR-002 on 2026-11-04.")
        self.assertEqual(summary_of(ch, "CHANGES.md", "# Changes\n"),
                         "Change log `CHANGES.md`: no change requests yet.")

    def test_summary_without_decisions(self):
        text = CHANGES.split("## CR-001")[0] + "## CR-003" + CHANGES.split("## CR-003")[1]
        self.assertEqual(summary_of(ch, "CHANGES.md", text),
                         "Change log `CHANGES.md`: 2 open (1 proposed, 1 assessed), 0 decided.")

    def test_summary_missing_and_invalid(self):
        self.assertEqual(summary_of(ch, "CHANGES.md", None), "Change log `CHANGES.md` is declared but missing: "
                         "run /pm-skills:change-request to create it.")
        self.assertEqual(summary_of(ch, "CHANGES.md", replaced(CHANGES, "Status: proposed", "Status: open")),
                         "Change log `CHANGES.md` has 1 validation error: run /pm-skills:change-request to fix them.")


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
                 ("decisions_register.py", DECISIONS, "accepted", "maybe"),
                 ("stakeholders_register.py", STAKEHOLDERS, "| high | high |", "| top | high |"),
                 ("capacity_register.py", CAPACITY, "| 50 |", "| 150 |"),
                 ("changes_register.py", CHANGES, "Status: proposed", "Status: open"))
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


class AsciiIds(unittest.TestCase):
    """IDs and references take ASCII digits only: `\\d` would also accept other scripts' digits."""

    def test_non_ascii_digits_are_rejected(self):
        cases = [
            (sr.validate, STAKEHOLDERS, "S-001", "S-\u0660\u0660\u0661"),
            (ch.validate, CHANGES, "## CR-001", "## CR-\u0660\u0660\u0661"),
            (rr.validate, RISKS, "R-001", "R-\u0660\u0660\u0661"),
            (dr.validate, DECISIONS, "## D-001", "## D-\u0660\u0660\u0661"),
        ]
        for validate, text, old, new in cases:
            with self.subTest(old=old):
                self.assertNotEqual(validate(replaced(text, old, new)), [])


class RobustReading(unittest.TestCase):
    """A register that cannot be decoded or summed up is reported, never a traceback."""

    def test_validate_of_a_file_that_is_not_utf8_is_an_io_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.md"
            bad.write_bytes(b"\xff\xfe\x00bad \x80\x81\n")
            for script in ("risks_register.py", "capacity_register.py", "changes_register.py"):
                with self.subTest(script=script):
                    result = subprocess.run([sys.executable, str(SCRIPTS / script), "validate", str(bad)],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertIn("cannot read", result.stderr)

    def test_arithmetic_error_in_one_register_does_not_hide_the_others(self):
        import decimal
        from unittest import mock

        import budget_register
        import registers

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "AGENTS.md").write_text("# Rules\n\n- Project register: `PROJECT.md`\n", encoding="utf-8")
            for name in ("PROJECT.md", "TEAMS.md", "BUDGET.md"):
                (project / name).write_text(fixture_text(name), encoding="utf-8")
            with mock.patch.object(budget_register, "summary_line", side_effect=decimal.InvalidOperation):
                line = registers.summary(project, TODAY)
        self.assertIn("Budget register `BUDGET.md` cannot be read", line)
        self.assertIn("Team register `TEAMS.md`", line)
