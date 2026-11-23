import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from _support import SCRIPTS, fixture_text

import teams_register as tr

FIXTURE = fixture_text()


def edited(old: str, new: str) -> str:
    assert old in FIXTURE, old
    return FIXTURE.replace(old, new, 1)


class ValidRegister(unittest.TestCase):
    def test_fixture_is_valid(self):
        self.assertEqual(tr.validate(FIXTURE), [])

    def test_parse_returns_members_and_periods(self):
        register, errors = tr.parse(FIXTURE)
        self.assertEqual(errors, [])
        self.assertEqual([m.slug for m in register.active], ["ada-l", "bo-k", "cy-t"])
        ada = register.active[0]
        self.assertEqual(ada.roles, ("developer", "reviewer"))
        self.assertEqual(ada.areas, ("api", "data model"))
        self.assertEqual(ada.line, 10)
        self.assertEqual(register.active[2].jira, "")
        self.assertEqual(register.last_reconciled, date(2026, 11, 20))
        self.assertEqual(register.sources, ("github:acme/web", "github:acme/api", "jira:ACME"))
        self.assertEqual(len(register.history), 5)
        self.assertIsNone(register.history[0].end)
        self.assertEqual(register.history[2].end, date(2026, 5, 31))

    def test_rejoin_two_periods_valid(self):
        register, errors = tr.parse(FIXTURE)
        self.assertEqual(errors, [])
        self.assertEqual(len([p for p in register.history if p.slug == "cy-t"]), 2)

    def test_role_change_closes_the_day_before(self):
        text = edited("| ada-l | 2026-01-12 |  | developer |",
                      "| ada-l | 2026-01-12 | 2026-11-22 | developer |\n| ada-l | 2026-11-23 |  | tech lead |")
        self.assertEqual(tr.validate(text), [])

    def test_optional_preamble_lines(self):
        text = edited("Last reconciled: 2026-11-20\nSources: github:acme/web, github:acme/api, jira:ACME\n", "")
        register, errors = tr.parse(text)
        self.assertEqual(errors, [])
        self.assertIsNone(register.last_reconciled)
        self.assertEqual(register.sources, ())

    def test_accepts_dates_and_jira_ids_not_as_phone(self):
        self.assertEqual(tr.validate(FIXTURE), [])


class Rejections(unittest.TestCase):
    def assertError(self, text: str, line: int, keyword: str):
        errors = tr.validate(text)
        matching = [e for e in errors if e.startswith(f"line {line}:") and keyword in e]
        self.assertTrue(matching, f"no 'line {line}: …{keyword}…' in {errors}")

    def test_rejects_free_text_line(self):
        self.assertError(edited("## History\n", "Ada is on leave next week.\n\n## History\n"), 14, "unexpected content")

    def test_rejects_missing_section(self):
        errors = tr.validate(FIXTURE.split("## History")[0])
        self.assertTrue(any("History" in e and "missing" in e for e in errors), errors)

    def test_rejects_extra_column(self):
        text = edited("| Slug | Name | Organization | GitHub | Jira | Roles | Areas |",
                      "| Slug | Name | Organization | GitHub | Jira | Roles | Areas | Phone |")
        self.assertError(text, 8, "columns")

    def test_rejects_extra_cell_in_row(self):
        self.assertError(edited("| web, ux |", "| web, ux | extra |"), 11, "cells")

    def test_rejects_duplicate_slug(self):
        self.assertError(edited("| bo-k | Bo K.", "| ada-l | Bo K."), 11, "duplicate")

    def test_rejects_bad_slug(self):
        self.assertError(edited("| bo-k | Bo K.", "| Bo_K | Bo K."), 11, "slug")

    def test_rejects_empty_name(self):
        self.assertError(edited("| Bo K. |", "|  |"), 11, "name")

    def test_rejects_github_with_at(self):
        self.assertError(edited("| bok |", "| @bok |"), 11, "GitHub")

    def test_rejects_jira_with_space(self):
        self.assertError(edited("| 5b10ac8d82e05b22cc7d4ef5 |", "| Ada L |"), 10, "Jira")

    def test_rejects_email_in_any_cell(self):
        self.assertError(edited("| api, data model |", "| api, ada@example.com |"), 10, "email")

    def test_rejects_phone_in_areas(self):
        self.assertError(edited("| api, data model |", "| api, +39 333 123 4567 |"), 10, "phone")

    def test_rejects_empty_roles(self):
        self.assertError(edited("| designer |", "|  |"), 11, "Roles")

    def test_rejects_empty_list_item(self):
        self.assertError(edited("| web, ux |", "| web, , ux |"), 11, "Areas")

    def test_rejects_bad_date(self):
        self.assertError(edited("| ada-l | 2026-01-12 |", "| ada-l | 12/01/2026 |"), 18, "date")

    def test_rejects_from_after_to(self):
        self.assertError(edited("| cy-t | 2026-03-01 | 2026-05-31 |", "| cy-t | 2026-06-01 | 2026-05-31 |"), 20, "after")

    def test_rejects_active_without_open_period(self):
        self.assertError(edited("| bo-k | 2026-02-01 |  |", "| bo-k | 2026-02-01 | 2026-03-01 |"), 11, "open period")

    def test_rejects_two_open_periods(self):
        self.assertError(edited("| cy-t | 2026-03-01 | 2026-05-31 |", "| cy-t | 2026-03-01 |  |"), 12, "open period")

    def test_rejects_open_period_for_former_member(self):
        self.assertError(edited("| di-r | 2026-01-12 | 2026-06-30 |", "| di-r | 2026-01-12 |  |"), 22, "not in Active team")

    def test_rejects_overlapping_periods(self):
        self.assertError(edited("| cy-t | 2026-09-01 |", "| cy-t | 2026-05-01 |"), 21, "overlaps")

    def test_rejects_period_starting_the_day_the_previous_ends(self):
        text = edited("| ada-l | 2026-01-12 |  | developer |",
                      "| ada-l | 2026-01-12 | 2026-11-23 | developer |\n| ada-l | 2026-11-23 |  | tech lead |")
        self.assertError(text, 19, "overlaps")

    def test_rejects_duplicate_github_login(self):
        self.assertError(edited("| bok |", "| ADAL |"), 11, "GitHub 'ADAL' is also on line 10")

    def test_rejects_duplicate_jira_account(self):
        self.assertError(edited("| 712020:1f2e3d4c-aaaa-bbbb-cccc-0123456789ab |", "| 5b10ac8d82e05b22cc7d4ef5 |"),
                         11, "Jira '5b10ac8d82e05b22cc7d4ef5' is also on line 10")

    def test_accepts_dates_and_year_ranges_in_text(self):
        text = edited("| api, data model |", "| api, release 2026-11-20 |").replace(
            "| ada-l | 2026-01-12 |  | developer |", "| ada-l | 2026-01-12 |  | developer 2024-2025 |")
        self.assertEqual(tr.validate(text), [])

    def test_accepts_numeric_github_login(self):
        self.assertEqual(tr.validate(edited("| bok |", "| u1234567890 |")), [])

    def test_rejects_phone_next_to_a_date(self):
        self.assertError(edited("| api, data model |", "| api 2026-11-20, call 333 123 4567 |"), 10, "phone")

    def test_rejects_bad_source(self):
        self.assertError(edited("jira:ACME", "jira:acme"), 4, "source")

    def test_rejects_bad_last_reconciled(self):
        self.assertError(edited("Last reconciled: 2026-11-20", "Last reconciled: yesterday"), 3, "date")


GIT_FIXTURE = FIXTURE.replace(
    "| Slug | Name | Organization | GitHub | Jira | Roles | Areas |\n|---|---|---|---|---|---|---|",
    "| Slug | Name | Organization | GitHub | Jira | Git | Roles | Areas |\n|---|---|---|---|---|---|---|---|",
).replace("| 5b10ac8d82e05b22cc7d4ef5 |", "| 5b10ac8d82e05b22cc7d4ef5 | ada@acme.example, ada.l@users.noreply.github.com |"
).replace("| 712020:1f2e3d4c-aaaa-bbbb-cccc-0123456789ab |", "| 712020:1f2e3d4c-aaaa-bbbb-cccc-0123456789ab |  |"
).replace("| cyt |  |", "| cyt |  | cy@initech.example |")


class GitColumn(unittest.TestCase):
    def test_accepts_git_column_with_commit_emails(self):
        self.assertEqual(tr.validate(GIT_FIXTURE), [])

    def test_parse_git_identities(self):
        register, _ = tr.parse(GIT_FIXTURE)
        self.assertEqual(register.active[0].git, ("ada@acme.example", "ada.l@users.noreply.github.com"))
        self.assertEqual(register.active[1].git, ())

    def test_git_is_empty_without_the_column(self):
        register, _ = tr.parse(FIXTURE)
        self.assertEqual(register.active[0].git, ())

    def test_rejects_non_email_in_git(self):
        errors = tr.validate(GIT_FIXTURE.replace("| cy@initech.example |", "| Cy T. |"))
        self.assertTrue(any(e.startswith("line 12:") and "Git" in e for e in errors), errors)

    def test_still_rejects_email_outside_git(self):
        errors = tr.validate(GIT_FIXTURE.replace("| api, data model |", "| api, ada@acme.example |"))
        self.assertTrue(any(e.startswith("line 10:") and "email" in e for e in errors), errors)

    def test_rejects_duplicate_git_identity(self):
        errors = tr.validate(GIT_FIXTURE.replace("| cy@initech.example |", "| ADA@acme.example |"))
        self.assertTrue(any(e.startswith("line 12:") and "is also on line 10" in e for e in errors), errors)


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "teams_register.py"), *args],
                              capture_output=True, text=True)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "TEAMS.md"
            good.write_text(FIXTURE, encoding="utf-8")
            bad = Path(tmp) / "BAD.md"
            bad.write_text(edited("| bok |", "| @bok |"), encoding="utf-8")
            self.assertEqual(self.run_cli("validate", str(good)).returncode, 0)
            result = self.run_cli("validate", str(bad))
            self.assertEqual(result.returncode, 1)
            self.assertIn("line 11:", result.stdout)
            self.assertEqual(self.run_cli("validate", str(Path(tmp) / "none.md")).returncode, 2)
            self.assertEqual(self.run_cli("frobnicate").returncode, 2)


if __name__ == "__main__":
    unittest.main()
