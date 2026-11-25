"""Tests of the life-cycle registers: the RACI matrix (RACI.md) and the gate register (GATES.md)."""
from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path
from typing import Optional

from _support import fixture_text

import gates_register as ga
import raci_register as ra

RACI = fixture_text("RACI.md")
GATES = fixture_text("GATES.md")
TODAY = date(2026, 11, 23)


def replaced(text: str, old: str, new: str) -> str:
    assert old in text, old
    return text.replace(old, new, 1)


class ErrorAssertions(unittest.TestCase):
    def assertError(self, errors: list[str], line: int, keyword: str) -> None:
        matching = [e for e in errors if e.startswith(f"line {line}:") and keyword in e]
        self.assertTrue(matching, f"no 'line {line}: …{keyword}…' in {errors}")


def summary_of(module, name: str, text: Optional[str], today: date = TODAY) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        if text is not None:
            path.write_text(text, encoding="utf-8")
        return module.summary_line(path, today, label=name)


class RaciRegister(ErrorAssertions):
    def test_fixture_is_valid(self):
        register, errors = ra.parse(RACI)
        self.assertEqual(errors, [])
        self.assertEqual(register.roles, ("Sponsor", "Product owner", "Tech lead", "Developers", "Security office"))
        self.assertEqual([r.id for r in register.rows], ["RA-001", "RA-002", "RA-003"])
        self.assertEqual(register.rows[0].cells["Tech lead"], "R")
        self.assertEqual(register.rows[2].wbs, "")

    def test_rejects_two_accountable(self):
        text = replaced(RACI, "| I | A | R | R | C |", "| I | A | A/R | R | C |")
        self.assertError(ra.validate(text), 5, "exactly one A")

    def test_rejects_no_accountable(self):
        text = replaced(RACI, "| I | A | R | R | C |", "| I | C | R | R | C |")
        errors = ra.validate(text)
        self.assertError(errors, 5, "RA-001")
        self.assertError(errors, 5, "exactly one A")

    def test_rejects_no_responsible(self):
        text = replaced(RACI, "|  | A | C | R | I |", "|  | A | C | I | I |")
        self.assertError(ra.validate(text), 7, "at least one R")

    def test_a_r_counts_as_both(self):
        text = RACI + "| RA-004 | Monitoring |  | A/R | I |  |  |  |\n"
        self.assertEqual(ra.validate(text), [])

    def test_rejects_bad_cell(self):
        text = replaced(RACI, "| I | A | R | R | C |", "| X | A | R | RA | C |")
        errors = ra.validate(text)
        self.assertError(errors, 5, "R, A, C, I, A/R")
        self.assertEqual(len([e for e in errors if "R, A, C, I, A/R" in e]), 2, errors)

    def test_rejects_bad_ids_and_wbs(self):
        text = replaced(RACI, "| RA-001 | Payment flow | 1.2 |", "| RA-1 | Payment flow | 1..2 |")
        text = replaced(text, "| RA-003 | Release notes |  |", "| RA-002 | Release notes | 1.٢ |")
        errors = ra.validate(text)
        self.assertError(errors, 5, "RA-1")
        self.assertError(errors, 5, "WBS '1..2'")
        self.assertError(errors, 7, "duplicate ID 'RA-002'")
        self.assertError(errors, 7, "WBS '1.٢'")

    def test_rejects_unicode_digits_in_id(self):
        text = replaced(RACI, "| RA-001 |", "| RA-٠٠١ |")
        self.assertError(ra.validate(text), 5, "RA-")

    def test_rejects_header_prefix(self):
        text = replaced(RACI, "| ID | Deliverable | WBS |", "| Deliverable | ID | WBS |")
        self.assertError(ra.validate(text), 3, "columns must start with: ID | Deliverable | WBS")

    def test_rejects_fewer_than_two_roles(self):
        text = "# RACI\n\n| ID | Deliverable | WBS | Tech lead |\n|---|---|---|---|\n| RA-001 | X |  | A/R |\n"
        self.assertError(ra.validate(text), 3, "at least two role columns")

    def test_rejects_duplicate_and_empty_role(self):
        text = replaced(RACI, "| Developers | Security office |", "| Tech lead |  |")
        errors = ra.validate(text)
        self.assertError(errors, 3, "duplicate role 'Tech lead'")
        self.assertError(errors, 3, "empty role")

    def test_rejects_wrong_cell_count_without_crashing(self):
        text = replaced(RACI, "| I | A | R | R | C |", "| I | A | R | R | C | |")
        self.assertError(ra.validate(text), 5, "expected 8 cells")

    def test_rejects_extra_content(self):
        self.assertError(ra.validate(RACI + "\nSee the charter.\n"), 9, "unexpected content")

    def test_rejects_missing_title_and_table(self):
        errors = ra.validate("")
        self.assertTrue(any("missing title" in e for e in errors), errors)
        self.assertTrue(any("missing the RACI table" in e for e in errors), errors)

    def test_rejects_contacts(self):
        text = replaced(RACI, "| Release notes |", "| Release notes ada@acme.example |")
        self.assertError(ra.validate(text), 7, "email address")

    def test_quantities_are_not_phone_numbers(self):
        text = replaced(RACI, "| Release notes |", "| Load test at 1 000 000 requests per day |")
        self.assertEqual(ra.validate(text), [])

    def test_summary(self):
        self.assertEqual(summary_of(ra, "RACI.md", RACI), "RACI matrix `RACI.md`: 3 deliverables, 5 roles.")

    def test_summary_missing(self):
        self.assertEqual(summary_of(ra, "RACI.md", None),
                         "RACI matrix `RACI.md` is declared but missing: run /pm-skills:raci-matrix to create it.")

    def test_summary_invalid(self):
        text = replaced(RACI, "| I | A | R | R | C |", "| I | C | R | R | C |")
        self.assertEqual(summary_of(ra, "RACI.md", text),
                         "RACI matrix `RACI.md` has 1 validation error: run /pm-skills:raci-matrix to fix them.")


EMPTY_GATES = """# Gates

## Gates

| ID | Gate | Milestone | Planned | Status |
|---|---|---|---|---|

## Criteria

| Gate | # | Criterion |
|---|---|---|

## Outcomes

| Gate | Date | Outcome | Decided by | Conditions | Review |
|---|---|---|---|---|---|
"""
HOLD_ROW = "| G-002 | 2026-11-13 | hold | steering committee | Criterion 3 not met | ACME-GR-002.md |\n"


def gates_with(*outcomes: str, status: str = "open") -> str:
    text = replaced(GATES, "| 2026-11-27 | open |", f"| 2026-11-27 | {status} |")
    return text + "".join(f"{row}\n" for row in outcomes)


class GateRegister(ErrorAssertions):
    def test_fixture_is_valid(self):
        register, errors = ga.parse(GATES)
        self.assertEqual(errors, [])
        self.assertEqual([g.id for g in register.gates], ["G-001", "G-002"])
        self.assertEqual(register.gates[1].planned, date(2026, 11, 27))
        self.assertEqual([(c.gate, c.number) for c in register.criteria],
                         [("G-001", 1), ("G-002", 1), ("G-002", 2), ("G-002", 3)])
        self.assertEqual(register.outcomes[1].outcome, "hold")
        self.assertEqual(register.outcomes[1].review, "ACME-GR-002.md")

    def test_empty_register_is_valid(self):
        self.assertEqual(ga.validate(EMPTY_GATES), [])

    def test_rejects_missing_section(self):
        text = replaced(GATES, "## Criteria\n", "")
        errors = ga.validate(text)
        self.assertTrue(any("missing section '## Criteria'" in e for e in errors), errors)

    def test_rejects_sections_out_of_order(self):
        text = EMPTY_GATES.replace("## Criteria", "## Tmp").replace("## Outcomes", "## Criteria").replace(
            "## Tmp", "## Outcomes")
        errors = ga.validate(text)
        self.assertTrue(any("out of order" in e for e in errors), errors)

    def test_rejects_bad_gate_values(self):
        text = replaced(GATES, "| G-001 | Discovery exit | A-004 | 2026-03-13 | passed |",
                        "| G-1 | Discovery exit | B-004 | 2026-13-01 | closed |")
        errors = ga.validate(text)
        self.assertError(errors, 7, "G-1")
        self.assertError(errors, 7, "Milestone 'B-004'")
        self.assertError(errors, 7, "Planned")
        self.assertError(errors, 7, "Status 'closed'")

    def test_rejects_unicode_digits(self):
        text = replaced(GATES, "| G-002 | Go-live readiness |", "| G-٠٠٢ | Go-live readiness |")
        text = replaced(text, "| G-002 | 3 |", "| G-002 | ٣ |")
        errors = ga.validate(text)
        self.assertError(errors, 8, "G-")
        self.assertError(errors, 17, "#")

    def test_rejects_bad_criterion_number(self):
        text = replaced(GATES, "| G-002 | 3 |", "| G-002 | 0 |")
        self.assertError(ga.validate(text), 17, "#")

    def test_rejects_duplicate_criterion_number(self):
        text = replaced(GATES, "| G-002 | 3 |", "| G-002 | 2 |")
        self.assertError(ga.validate(text), 17, "duplicate criterion 2")

    def test_rejects_unknown_gate(self):
        text = replaced(GATES, "| G-002 | 3 |", "| G-009 | 3 |")
        text = replaced(text, "| G-002 | 2026-11-13 |", "| G-009 | 2026-11-13 |")
        errors = ga.validate(text)
        self.assertError(errors, 17, "unknown gate 'G-009'")
        self.assertError(errors, 24, "unknown gate 'G-009'")

    def test_rejects_gate_without_criteria(self):
        text = replaced(GATES, "| G-001 | 1 | Product Goal and first release scope approved by the sponsor |\n", "")
        self.assertError(ga.validate(text), 7, "no criteria")

    def test_rejects_duplicate_gate_id(self):
        text = replaced(GATES, "| G-002 | Go-live readiness |", "| G-001 | Go-live readiness |")
        self.assertError(ga.validate(text), 8, "duplicate ID 'G-001'")

    def test_rejects_bad_outcome(self):
        text = replaced(GATES, "| 2026-11-13 | hold |", "| 2026-11-13 | approved |")
        self.assertError(ga.validate(text), 24, "Outcome 'approved'")

    def test_conditions_required(self):
        text = replaced(GATES, "| hold | steering committee | Criterion 3 not met |", "| hold | steering committee |  |")
        self.assertError(ga.validate(text), 24, "Conditions")
        text = gates_with("| G-002 | 2026-11-27 | go with conditions | steering committee |  | ACME-GR-003.md |",
                          status="passed")
        self.assertError(ga.validate(text), 25, "Conditions")

    def test_decided_by_required(self):
        text = replaced(GATES, "| hold | steering committee |", "| hold |  |")
        self.assertError(ga.validate(text), 24, "Decided by")

    def test_status_consistency(self):
        text = replaced(GATES, "| 2026-11-27 | open |", "| 2026-11-27 | passed |")
        self.assertError(ga.validate(text), 8, "Status 'passed' must be 'open'")

    def test_no_outcome_after_go(self):
        text = GATES + "| G-001 | 2026-04-01 | hold | steering committee | Rework | ACME-GR-004.md |\n"
        self.assertError(ga.validate(text), 25, "no outcome may follow 'go'")

    def test_no_outcome_after_stop(self):
        text = gates_with("| G-002 | 2026-11-20 | stop | steering committee |  |  |",
                          "| G-002 | 2026-11-27 | go | steering committee |  |  |", status="passed")
        self.assertError(ga.validate(text), 26, "no outcome may follow 'stop'")

    def test_go_after_go_with_conditions(self):
        text = gates_with("| G-002 | 2026-11-27 | go with conditions | steering committee | Pen test fixes by "
                          "2026-12-11 (criterion 3) | ACME-GR-003.md |",
                          "| G-002 | 2026-12-11 | go | steering committee |  |  |", status="passed")
        self.assertEqual(ga.validate(text), [])

    def test_stop_after_hold(self):
        text = gates_with("| G-002 | 2026-11-20 | stop | sponsor |  |  |", status="stopped")
        self.assertEqual(ga.validate(text), [])

    def test_date_order(self):
        text = gates_with("| G-002 | 2026-11-01 | hold | steering committee | Still open |  |")
        self.assertError(ga.validate(text), 25, "date order")
        text = gates_with("| G-002 | 2026-11-13 | hold | steering committee | Still open |  |")
        self.assertEqual(ga.validate(text), [])

    def test_rejects_extra_content(self):
        text = replaced(GATES, "## Criteria\n", "Gates are decided by the steering committee.\n\n## Criteria\n")
        self.assertError(ga.validate(text), 10, "unexpected content")

    def test_quantities_are_not_phone_numbers(self):
        text = replaced(GATES, "| Release scope meets the Definition of Done |",
                        "| Load test passed at 1 000 000 requests per day |")
        text = replaced(text, "| Criterion 3 not met |", "| Rerun the load test at 100 000 000 requests |")
        self.assertEqual(ga.validate(text), [])

    def test_rejects_contacts(self):
        text = replaced(GATES, "| hold | steering committee |", "| hold | ada@acme.example |")
        self.assertError(ga.validate(text), 24, "email address")

    def test_summary(self):
        self.assertEqual(summary_of(ga, "GATES.md", GATES),
                         "Gate register `GATES.md`: 2 gates (1 passed, 1 open), next G-002 planned 2026-11-27.")

    def test_summary_past_planned_date(self):
        self.assertEqual(summary_of(ga, "GATES.md", GATES, date(2026, 11, 30)),
                         "Gate register `GATES.md`: 2 gates (1 passed, 1 open), next G-002 planned 2026-11-27, "
                         "past its planned date: run /pm-skills:phase-gate-review.")

    def test_summary_no_open_gate(self):
        text = gates_with("| G-002 | 2026-11-27 | go | steering committee |  |  |", status="passed")
        self.assertEqual(summary_of(ga, "GATES.md", text),
                         "Gate register `GATES.md`: 2 gates (2 passed), no open gate.")

    def test_summary_empty_and_missing_and_invalid(self):
        self.assertEqual(summary_of(ga, "GATES.md", EMPTY_GATES), "Gate register `GATES.md`: no gates yet.")
        self.assertEqual(summary_of(ga, "GATES.md", None), "Gate register `GATES.md` is declared but missing: "
                                                           "run /pm-skills:phase-gate-review to create it.")
        text = replaced(GATES, "| 2026-11-27 | open |", "| 2026-11-27 | closed |")
        self.assertEqual(summary_of(ga, "GATES.md", text), "Gate register `GATES.md` has 1 validation error: "
                                                           "run /pm-skills:phase-gate-review to fix them.")


if __name__ == "__main__":
    unittest.main()
