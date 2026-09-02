"""Tests for roster_parser.

Run with:  python -m unittest discover -s tests
Requires openpyxl (see requirements.txt).
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl

from roster_parser import (
    RosterError,
    parse_course_from_filename,
    parse_registration_summary,
    parse_student_cell,
    read_roster,
)

HEADERS = [
    "Student Course Registration",
    "Photo",
    "Student",
    "Pronoun",
    "Email Address",
    "Credits",
    "Academic Level",
    "Academic Unit",
    "Program of Study",
    "Registration Status",
]

ROW_JANE = [
    "Jane Doe (1234567) - Division/status (AA) - 08/15/2026 - Active - "
    "SOC 2210 - Sociology of Deviance - 2026 Autumn Semester",
    "Photo",
    "Jane Doe (1234567)",
    "She/Her/Hers",
    "doe1@student.cscc.edu",
    3,
    "Undergraduate",
    "Arts and Sciences",
    "Associate of Arts",
    "Registered",
]

ROW_JOHN = [
    "John Smith (7654321) - Arts and Sciences/Undergraduate (AS) - 08/16/2026 - "
    "Active - SOC 2210 - Sociology of Deviance - 2026 Autumn Semester",
    "Photo",
    "John Smith (7654321)",
    "He/Him/His",
    "Smith10@student.cscc.edu",
    3,
    "Undergraduate",
    "Arts and Sciences",
    "Associate of Science",
    "Registered",
]


def make_workbook(path, header_offset=0, rows=(ROW_JANE, ROW_JOHN)):
    wb = openpyxl.Workbook()
    ws = wb.active
    for _ in range(header_offset):
        ws.append(["Report generated 09/02/2026"])
    ws.append(HEADERS)
    for row in rows:
        ws.append(row)
    ws.append([None] * len(HEADERS))  # trailing blank row
    wb.save(path)


class FilenameTests(unittest.TestCase):
    def test_dash_separated(self):
        self.assertEqual(
            parse_course_from_filename("SOC-2210-W01.xlsx"), ("SOC", "2210", "W01")
        )

    def test_underscore_separated(self):
        self.assertEqual(
            parse_course_from_filename("ENGL_1100_H02.xlsx"),
            ("ENGL", "1100", "H02"),
        )

    def test_unparseable(self):
        self.assertEqual(
            parse_course_from_filename("roster.xlsx"), ("roster", "", "")
        )


class StudentCellTests(unittest.TestCase):
    def test_name_and_id(self):
        self.assertEqual(parse_student_cell("Jane Doe (1234567)"), ("Jane Doe", "1234567"))

    def test_name_only(self):
        self.assertEqual(parse_student_cell("Jane Doe"), ("Jane Doe", ""))

    def test_empty(self):
        self.assertEqual(parse_student_cell(""), ("", ""))


class SummaryTests(unittest.TestCase):
    def test_full_summary(self):
        result = parse_registration_summary(ROW_JANE[0])
        self.assertEqual(result["course_code"], "SOC 2210")
        self.assertEqual(result["course_title"], "Sociology of Deviance")
        self.assertEqual(result["term"], "2026 Autumn Semester")
        self.assertEqual(result["status"], "Active")

    def test_empty(self):
        result = parse_registration_summary("")
        self.assertEqual(result["course_code"], "")
        self.assertEqual(result["term"], "")


class ReadRosterTests(unittest.TestCase):
    def _read(self, **kwargs):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "SOC-2210-W01.xlsx")
            make_workbook(path, **kwargs)
            return read_roster(path)

    def test_basic(self):
        records = self._read()
        self.assertEqual(len(records), 2)
        jane = records[0]
        self.assertEqual(jane["student_name"], "Jane Doe")
        self.assertEqual(jane["student_id"], "1234567")
        self.assertEqual(jane["pronoun"], "She/Her/Hers")
        self.assertEqual(jane["email"], "doe1@student.cscc.edu")
        self.assertEqual(jane["course"], "SOC")
        self.assertEqual(jane["course_number"], "2210")
        self.assertEqual(jane["section"], "W01")
        self.assertEqual(jane["course_code"], "SOC 2210")
        self.assertEqual(jane["course_title"], "Sociology of Deviance")
        self.assertEqual(jane["term"], "2026 Autumn Semester")
        self.assertEqual(jane["credits"], "3")
        self.assertEqual(jane["academic_level"], "Undergraduate")
        self.assertEqual(jane["program_of_study"], "Associate of Arts")
        self.assertEqual(jane["registration_status"], "Registered")
        self.assertEqual(jane["source_file"], "SOC-2210-W01.xlsx")

    def test_header_not_on_first_row(self):
        records = self._read(header_offset=3)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[1]["student_name"], "John Smith")

    def test_rejects_non_xlsx(self):
        with self.assertRaises(RosterError):
            read_roster("something.csv")

    def test_missing_headers(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "SOC-2210-W01.xlsx")
            wb = openpyxl.Workbook()
            wb.active.append(["Foo", "Bar"])
            wb.active.append(["a", "b"])
            wb.save(path)
            with self.assertRaises(RosterError):
                read_roster(path)


if __name__ == "__main__":
    unittest.main()
