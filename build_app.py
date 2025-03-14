import sys
import os
import platform
import subprocess

def build_app():
    """Build the application using PyInstaller for the current platform"""
    
    # Common PyInstaller arguments
    base_args = [
        "pyinstaller",
        "--name=Student_Lookup",
        "--onefile",
        "--noconsole",
        "--clean",
    ]
    
    # Platform-specific arguments
    if platform.system() == "Windows":
        # Windows-specific settings
        icon_arg = "--icon=Student_Lookup.ico"
        base_args.append(icon_arg)
        version_file = "--version-file=version.txt"
        if os.path.exists("version.txt"):
            base_args.append(version_file)
    
    elif platform.system() == "Darwin":
        # macOS-specific settings
        icon_arg = "--icon=Student_Lookup.icns"
        if os.path.exists("Student_Lookup.icns"):
            base_args.append(icon_arg)
    
    # Add the main script
    base_args.append("Student_Lookup.py")
    
    # Run PyInstaller
    print(f"Building with command: {' '.join(base_args)}")
    subprocess.run(base_args)
    
    print("\nBuild completed!")
    if platform.system() == "Windows":
        print("Your executable is in the dist folder: dist/Student_Lookup.exe")
    elif platform.system() == "Darwin":
        print("Your application is in the dist folder: dist/Student_Lookup.app")
    else:
        print("Your executable is in the dist folder: dist/Student_Lookup")

if __name__ == "__main__":
    build_app()