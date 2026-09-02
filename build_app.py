import sys
import os
import platform
import subprocess

# roster_parser is imported by Student_Lookup at runtime; make sure PyInstaller
# picks it up along with anything it needs.
EXTRA_MODULES = ["roster_parser"]


def build_app():
    """Build the application using PyInstaller for the current platform"""

    # Run PyInstaller through the current interpreter so the build always uses
    # the same environment (and Python) that has the dependencies installed.
    base_args = [
        sys.executable, "-m", "PyInstaller",
        "--name=Student_Lookup",
        "--onefile",
        "--noconsole",
        "--clean",
        "--noconfirm",
        # Roster files are Excel workbooks; make sure openpyxl is bundled.
        "--hidden-import=openpyxl",
        "--collect-submodules=openpyxl",
    ]

    for module in EXTRA_MODULES:
        base_args.append(f"--hidden-import={module}")

    # Platform-specific arguments
    if platform.system() == "Windows":
        if os.path.exists("Student_Lookup.ico"):
            base_args.append("--icon=Student_Lookup.ico")
        if os.path.exists("version.txt"):
            base_args.append("--version-file=version.txt")

    elif platform.system() == "Darwin":
        if os.path.exists("Student_Lookup.icns"):
            base_args.append("--icon=Student_Lookup.icns")
        base_args.append("--osx-bundle-identifier=com.digiasati.Student_Lookup")

    # Add the main script
    base_args.append("Student_Lookup.py")

    # Run PyInstaller
    print(f"Building with command: {' '.join(base_args)}")
    result = subprocess.run(base_args)
    if result.returncode != 0:
        sys.exit(result.returncode)

    print("\nBuild completed!")
    if platform.system() == "Windows":
        print("Your executable is in the dist folder: dist/Student_Lookup.exe")
    elif platform.system() == "Darwin":
        print("Your application is in the dist folder: dist/Student_Lookup.app")
    else:
        print("Your executable is in the dist folder: dist/Student_Lookup")


if __name__ == "__main__":
    build_app()
