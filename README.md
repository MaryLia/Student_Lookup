## Student_Lookup
A Python/Tkinter based app to quickly look up course and section number by student name

## Requirements
- Python 3.x
- PyInstaller (if you want to build the .app)

## How to Run
1. Clone this repo: `git clone https://github.com/MaryLia/Student-Lookup.git`
2. `cd Student-Lookup`
3. `python3 Student_Lookup.py`

## How to Add Rosters
1. Download rosters from Cougarweb or from whatever source you have available.
2. Ensure the roster includes the following columns: Student Name | Student ID | Class Level | Student E-mail.  This should be the default from Cougarweb.
3. Rename your rosters so that they are titled something like Course Name - Course Number - Section Number.csv (eg Soc-101-W01.csv).
4. After running the app, click on "Add Rosters" and select the rosters you wish to add to the app.

## How to Search for Students
In the Search Student Name: area, begin typing the student's name. Highlight the student's name when it pops up below, then look at the bottom of the window and you will then see the student's course, section number and e-mail address. 

## How to Delete Rosters
Click on the Flush Data at the end of the semester to delete the old rosters from memory and prepare to add rosters for the next semester.
