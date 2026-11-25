"""Tests of the life-cycle registers: the RACI matrix (RACI.md) and the gate register (GATES.md)."""
from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path
from typing import Optional

from _support import fixture_text

import raci_register as ra

RACI = fixture_text("RACI.md")
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

    def test_summary(self):
        self.assertEqual(summary_of(ra, "RACI.md", RACI), "RACI matrix `RACI.md`: 3 deliverables, 5 roles.")

    def test_summary_missing(self):
        self.assertEqual(summary_of(ra, "RACI.md", None),
                         "RACI matrix `RACI.md` is declared but missing: run /pm-skills:raci-matrix to create it.")

    def test_summary_invalid(self):
        text = replaced(RACI, "| I | A | R | R | C |", "| I | C | R | R | C |")
        self.assertEqual(summary_of(ra, "RACI.md", text),
                         "RACI matrix `RACI.md` has 1 validation error: run /pm-skills:raci-matrix to fix them.")


if __name__ == "__main__":
    unittest.main()
