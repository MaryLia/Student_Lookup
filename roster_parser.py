"""Roster parsing for Student Lookup.

This module has no GUI dependencies so it can be unit tested on its own.
It reads the current roster export format: an Excel (.xlsx) file with one
course per file, where the course/section is taken from the file name and the
per-student details come from the spreadsheet columns.
"""

import os
import re

import openpyxl


class RosterError(Exception):
    """Raised when a roster file cannot be parsed."""


# Header cells we expect on the header row of the export. The first two are
# required; everything else is used when present.
REQUIRED_HEADERS = ("Student", "Email Address")

SUMMARY_HEADER = "Student Course Registration"

# e.g. "SOC 2210" or "ENGL 1100H"
COURSE_CODE_RE = re.compile(r"^[A-Za-z]{2,5}\s+\d{3,4}[A-Za-z]?$")

# "Jane Doe (1234567)"  ->  ("Jane Doe", "1234567")
NAME_ID_RE = re.compile(r"^\s*(.*?)\s*\((\d+)\)\s*$")


def parse_course_from_filename(filename):
    """Return (course, course_number, section) parsed from a roster file name.

    Expected shape is "Course-Number-Section.xlsx" (e.g. "SOC-2210-W01.xlsx").
    Separators may be '-', '_' or spaces. Falls back gracefully when the name
    does not match.
    """
    stem = os.path.splitext(os.path.basename(filename))[0]

    match = re.match(r"([A-Za-z]+)[-_ ]+(\w+)[-_ ]+(\w+)$", stem)
    if match:
        return match.group(1), match.group(2), match.group(3)

    parts = re.split(r"[-_ ]+", stem)
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]

    return stem, "", ""


def parse_student_cell(text):
    """Return (name, student_id) from a "Name (ID)" string."""
    if not text:
        return "", ""
    match = NAME_ID_RE.match(str(text))
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return str(text).strip(), ""


def parse_registration_summary(text):
    """Pull the course code, title and term out of the compound column A value.

    Example input:
        "Jane Doe (1234567) - Division/status (AA) - 08/15/2026 - Active - "
        "SOC 2210 - Sociology of Deviance - 2026 Autumn Semester"

    Returns a dict with keys: course_code, course_title, term, status.
    Missing pieces come back as "".
    """
    result = {"course_code": "", "course_title": "", "term": "", "status": ""}
    if not text:
        return result

    segments = [s.strip() for s in str(text).split(" - ")]
    if not segments:
        return result

    # The term is the last segment; the course code is the first segment that
    # looks like "SUBJ 1234"; the title is everything between them.
    result["term"] = segments[-1]

    code_index = None
    for i, seg in enumerate(segments):
        if COURSE_CODE_RE.match(seg):
            code_index = i
            break

    if code_index is not None:
        result["course_code"] = segments[code_index]
        title_parts = segments[code_index + 1:-1]
        if title_parts:
            result["course_title"] = " - ".join(title_parts)

    # The enrollment status ("Active" / "Dropped" ...) is the segment right
    # before the course code when the layout matches the known export.
    if code_index and code_index - 1 >= 0:
        result["status"] = segments[code_index - 1]

    return result


def _find_header_row(rows):
    """Return (index, header_list) for the first row that carries the headers."""
    for i, row in enumerate(rows):
        values = [str(c).strip() if c is not None else "" for c in row]
        if all(any(h == v for v in values) for h in REQUIRED_HEADERS):
            return i, values
    return None, None


def read_roster(file_path):
    """Read one roster .xlsx file and return a list of student record dicts."""
    if not str(file_path).lower().endswith(".xlsx"):
        raise RosterError("Not an .xlsx file")

    course, course_number, section = parse_course_from_filename(file_path)
    filename = os.path.basename(file_path)

    try:
        workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    except Exception as exc:  # openpyxl raises a variety of errors
        raise RosterError(f"Could not open workbook: {exc}") from exc

    try:
        sheet = workbook.active
        rows = [list(r) for r in sheet.iter_rows(values_only=True)]
    finally:
        workbook.close()

    header_index, headers = _find_header_row(rows)
    if header_index is None:
        raise RosterError(
            "Could not find a header row containing "
            + " and ".join(f'"{h}"' for h in REQUIRED_HEADERS)
        )

    col = {name: idx for idx, name in enumerate(headers) if name}

    def cell(row, name):
        idx = col.get(name)
        if idx is None or idx >= len(row):
            return ""
        value = row[idx]
        return "" if value is None else str(value).strip()

    records = []
    for row in rows[header_index + 1:]:
        if not any(c is not None and str(c).strip() for c in row):
            continue  # blank row

        student_name, student_id = parse_student_cell(cell(row, "Student"))
        summary = parse_registration_summary(cell(row, SUMMARY_HEADER))

        if not student_name:
            # Fall back to the name embedded in the summary column.
            student_name, summary_id = parse_student_cell(
                cell(row, SUMMARY_HEADER).split(" - ")[0]
            )
            student_id = student_id or summary_id

        if not student_name:
            continue

        records.append(
            {
                "course": course,
                "course_number": course_number,
                "section": section,
                "course_code": summary["course_code"],
                "course_title": summary["course_title"],
                "term": summary["term"],
                "student_name": student_name,
                "student_id": student_id,
                "pronoun": cell(row, "Pronoun"),
                "email": cell(row, "Email Address"),
                "credits": cell(row, "Credits"),
                "academic_level": cell(row, "Academic Level"),
                "academic_unit": cell(row, "Academic Unit"),
                "program_of_study": cell(row, "Program of Study"),
                "registration_status": cell(row, "Registration Status")
                or summary["status"],
                "source_file": filename,
            }
        )

    return records
