# Student_Lookup
A Python/Tkinter based app to quickly look up course and section numbers by student name. This should save time when a student e-mails you a question, but you don't know what class they are in.

# How to Install
If you want to compile it yourself, see below.
Easy download and install links are at the bottom of this page.

## Requirements
- Python 3.9+ with Tkinter (the python.org installers include it; on Homebrew, `brew install python-tk`)
- `openpyxl` (to read the Excel roster files)
- PyInstaller (only if you want to build the standalone app)

Install the dependencies with:

```
pip install -r requirements.txt
```

## How to Run from source
1. Clone this repo: `git clone https://github.com/MaryLia/Student_Lookup.git`
2. `cd Student_Lookup`
3. `pip install -r requirements.txt`
4. `python Student_Lookup.py`

## How to Build the standalone app

`python build_app.py` produces a single-file app for whatever OS you run it on:

| Build host | Output |
|------------|--------|
| Windows    | `dist/Student_Lookup.exe` |
| macOS      | `dist/Student_Lookup.app` |

PyInstaller cannot cross-compile, so a Windows `.exe` must be built on Windows
and a macOS `.app` on macOS. You don't need a second machine for this: the
GitHub Actions workflow in `.github/workflows/build.yml` builds Windows, macOS
(Intel) and macOS (Apple Silicon) on every push, and attaches all three to a
GitHub Release when you push a version tag:

```
git tag v2.0.0
git push origin v2.0.0
```

The build is unsigned, so the first launch needs a manual approval:
- **macOS:** right-click the app → **Open** → **Open** (or run `xattr -dr com.apple.quarantine Student_Lookup.app`).
- **Windows:** on the "Windows protected your PC" dialog, click **More info → Run anyway**.

# Instructions

## How to Add Rosters
1. Download each course roster as an Excel (`.xlsx`) file (one file per course/section) from Cougarweb or whatever source you have available.
2. Place the rosters in an easy to find folder (this folder will be referenced by the app). I call mine something like "SP25 Rosters" and keep it on my Onedrive.
3. The app reads these columns from the spreadsheet: `Student`, `Pronoun`, `Email Address`, `Credits`, `Academic Level`, `Academic Unit`, `Program of Study`, `Registration Status`, and the compound `Student Course Registration` column (used for the course title and term). `Student` and `Email Address` are required; the header row does not have to be the first row.
4. Rename your rosters so that they are titled `Course-Number-Section.xlsx` (e.g. `SOC-2210-W01.xlsx`). The course, number and section shown in the app come from the file name.
5. After running the app, click on "Load Rosters" and select the rosters you wish to add to the app.

## How to Search for Students
In the Search Student Name: area, begin typing the student's name. Highlight the student's name when it pops up below, then look at the right-hand pane to see the student's course, section, term, e-mail address and other details. 

## How to Delete Rosters
Click on the Flush Data at the end of the semester to delete the old rosters from memory and prepare to add rosters for the next semester.

## Download the Student Lookup App
Download the app on Dropbox here: [Student_Lookup.app for Mac and StudentLookupInstaller.exe for Windows](https://www.dropbox.com/scl/fo/kw9d7h9j8hh5ayhnib3au/AKnY_ZPavaijGPaKBV4cRUQ?rlkey=7qb1s3zttnvcxmd6tc1b4r88i&st=0pavdsn8&dl=0)
