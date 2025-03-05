# Student_Lookup
A Python/Tkinter based app to quickly look up course and section numbers by student name. This should save time when a student e-mails you a question, but you don't know what class they are in.

# How to Install
If you want to compile it yourself, see below.
Easy download and install links are at the bottom of this page.

## Requirements
- Python 3.x
- PyInstaller (if you want to build the .app)

## How to Run
1. Clone this repo: `git clone https://github.com/MaryLia/Student-Lookup.git`
2. `cd Student-Lookup`
3. `pyinstaller Student_Lookup.spec`

# Instructions

## How to Add Rosters
1. Download rosters from Cougarweb or from whatever source you have available.
2. Place the rosters in an easy to find folder (this folder will be referenced by the app). I call mine something like "SP25 Rosters" and keep it on my Onedrive.
3. Ensure the roster includes the following columns: Student Name | Student ID | Class Level | Student E-mail.  This should be the default from Cougarweb.
4. Rename your rosters so that they are titled something like Course Name - Course Number - Section Number.csv (eg Soc-101-W01.csv).
5. After running the app, click on "Add Rosters" and select the rosters you wish to add to the app.

## How to Search for Students
In the Search Student Name: area, begin typing the student's name. Highlight the student's name when it pops up below, then look at the bottom of the window and you will then see the student's course, section number and e-mail address. 

## How to Delete Rosters
Click on the Flush Data at the end of the semester to delete the old rosters from memory and prepare to add rosters for the next semester.

## Download the Student Lookup App
Download the app on Dropbox here: [Student_Lookup.app for Mac and StudentLookupInstaller.exe for Windows](https://www.dropbox.com/scl/fo/kw9d7h9j8hh5ayhnib3au/AKnY_ZPavaijGPaKBV4cRUQ?rlkey=7qb1s3zttnvcxmd6tc1b4r88i&st=0pavdsn8&dl=0)
