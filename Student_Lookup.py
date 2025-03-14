import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import csv
import json
import re
import sys
from pathlib import Path

# Version
APP_VERSION = "1.0.1"

# Get appropriate config path for different operating systems
def get_config_path():
    app_name = "StudentLookup"
    
    if sys.platform == "win32":  # Windows
        config_dir = Path(os.environ.get("LOCALAPPDATA", os.getcwd())) / app_name
    elif sys.platform == "darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / app_name
    else:  # Linux and others
        config_dir = Path.home() / ".config" / app_name
    
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Could not create config directory: {e}")
        config_dir = Path.cwd()
    
    return config_dir / "config.json"

CONFIG_FILE = get_config_path()

class StudentLookupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Basic window setup
        self.title(f"Student Lookup v{APP_VERSION}")
        self.geometry("700x500")
        self.minsize(600, 400)
        
        # Try to set icon based on platform
        self.set_app_icon()
        
        # Initialize data structures
        self.loaded_files = []       # List of file paths loaded
        self.student_records = []    # All student records
        self.matched_records = []    # Records that match current search
        
        # Load config if it exists
        self.load_config()
        
        # Build GUI
        self.create_widgets()
        
        # If config exists, auto-load the saved CSVs
        if self.loaded_files:
            self.load_rosters_from_files(self.loaded_files)
    
    def set_app_icon(self):
        """Set application icon based on platform"""
        try:
            if sys.platform == "win32" and os.path.exists("Student_Lookup.ico"):
                self.iconbitmap("Student_Lookup.ico")
            elif sys.platform == "darwin" and os.path.exists("Student_Lookup.icns"):
                # macOS uses .icns format
                self.iconbitmap("Student_Lookup.icns")
        except Exception as e:
            print(f"Could not set icon: {e}")
    
    def create_widgets(self):
        """Create and arrange all UI widgets"""
        self.create_menu()
        
        # Main frame to contain everything
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status bar for showing loaded files count
        self.status_var = tk.StringVar(value="No rosters loaded")
        status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Top control frame
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Load rosters button
        load_button = tk.Button(control_frame, text="Load Rosters", 
                               command=self.on_load_rosters, padx=10)
        load_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Flush data button
        flush_button = tk.Button(control_frame, text="Flush All Data", 
                                command=self.on_flush_data, padx=10)
        flush_button.pack(side=tk.LEFT)
        
        # Search frame
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Search Student Name:").pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)  # Trigger search as user types
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Results and details pane - split horizontally
        panes_frame = tk.Frame(main_frame)
        panes_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left pane - Results list
        results_frame = tk.LabelFrame(panes_frame, text="Search Results")
        results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.results_listbox = tk.Listbox(results_frame, height=15, activestyle='dotbox')
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_listbox.bind("<<ListboxSelect>>", self.on_select_student)
        
        # Scrollbar for results
        results_scrollbar = tk.Scrollbar(results_frame, orient="vertical", 
                                       command=self.results_listbox.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.config(yscrollcommand=results_scrollbar.set)
        
        # Right pane - Student details
        details_frame = tk.LabelFrame(panes_frame, text="Student Details")
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, 
                                                   width=40, height=10)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.details_text.config(state=tk.DISABLED)  # Make read-only
        
        # Set focus to search box
        self.search_entry.focus_set()
        
    def create_menu(self):
        """Create application menu"""
        menu_bar = tk.Menu(self)
        
        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Load Rosters", command=self.on_load_rosters)
        file_menu.add_command(label="View Loaded Files", command=self.show_loaded_files)
        file_menu.add_separator()
        file_menu.add_command(label="Flush All Data", command=self.on_flush_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Add menus to menu bar
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menu_bar)
    
    def on_load_rosters(self):
        """Open file dialog to load roster CSVs"""
        file_paths = filedialog.askopenfilenames(
            title="Select up to 9 roster CSV files",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_paths:
            return
        
        if len(file_paths) > 9:
            messagebox.showwarning(
                "Too Many Files", 
                "You can load up to 9 rosters at once. Only the first 9 will be used."
            )
            file_paths = file_paths[:9]
        
        # Store the new file paths
        self.loaded_files = list(file_paths)
        
        # Load rosters from these files
        self.load_rosters_from_files(self.loaded_files)
        
        # Save config
        self.save_config()
    
    def load_rosters_from_files(self, file_paths):
        """Load student data from the given CSV files"""
        # Clear existing records
        self.student_records = []
        successful_files = []
        failed_files = []
        
        for file_path in file_paths:
            try:
                # Extract course info from filename (e.g., "SOC-1101-W01.csv")
                filename = os.path.basename(file_path)
                
                # Try to extract course info from filename
                match = re.match(r"([A-Za-z]+)-(\w+)-(\w+)\.csv", filename)
                
                if match:
                    course = match.group(1)
                    course_number = match.group(2)
                    section = match.group(3)
                else:
                    # If filename doesn't match expected format, use filename parts
                    name_parts = filename.split(".")[0].split("-")
                    if len(name_parts) >= 3:
                        course = name_parts[0]
                        course_number = name_parts[1]
                        section = name_parts[2]
                    else:
                        # Use filename as course if no pattern matches
                        course = filename.split(".")[0]
                        course_number = ""
                        section = ""
                
                # Read CSV and extract student data
                with open(file_path, mode="r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    
                    # Check if required columns exist
                    first_row = next(reader, None)
                    if first_row is None:
                        raise ValueError("CSV file is empty")
                    
                    # Reset file pointer and recreate reader
                    f.seek(0)
                    reader = csv.DictReader(f)
                    
                    # Process each student row
                    for row in reader:
                        # Extract student info, handling variations in column names
                        student_name = (
                            row.get("Student Name", "") or 
                            row.get("Name", "") or 
                            ""
                        ).strip()
                        
                        student_id = (
                            row.get("Student ID", "") or 
                            row.get("ID", "") or 
                            ""
                        ).strip()
                        
                        class_level = (
                            row.get("Class Level", "") or 
                            row.get("Level", "") or 
                            ""
                        ).strip()
                        
                        email = (
                            row.get("Preferred Email", "") or 
                            row.get("Email", "") or 
                            ""
                        ).strip()
                        
                        # Skip rows with no student name
                        if not student_name:
                            continue
                        
                        # Create student record
                        record = {
                            "course": course,
                            "course_number": course_number,
                            "section": section,
                            "student_name": student_name,
                            "student_id": student_id,
                            "class_level": class_level,
                            "email": email,
                            "source_file": filename
                        }
                        
                        self.student_records.append(record)
                
                successful_files.append(filename)
                
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")
                failed_files.append(os.path.basename(file_path))
        
        # Update status bar
        self.update_status_bar()
        
        # Clear search box and results
        self.search_var.set("")
        self.update_search_results("")
        
        # Show messages about loading results
        if successful_files:
            loaded_msg = f"Successfully loaded {len(successful_files)} roster(s).\n"
            loaded_msg += f"Total students: {len(self.student_records)}"
            self.update_details_text(loaded_msg)
        
        if failed_files:
            messagebox.showwarning(
                "Loading Issues", 
                f"Failed to load {len(failed_files)} file(s):\n" + 
                "\n".join(failed_files)
            )
    
    def on_flush_data(self):
        """Remove all rosters and clear the config"""
        if messagebox.askyesno("Confirm", "Are you sure you want to flush all data?"):
            self.loaded_files = []
            self.student_records = []
            self.update_search_results("")
            self.update_details_text("All data flushed.")
            self.update_status_bar()
            
            # Remove config file if it exists
            if os.path.exists(CONFIG_FILE):
                try:
                    os.remove(CONFIG_FILE)
                except Exception as e:
                    print(f"Error removing config file: {e}")
    
    def on_search_change(self, *args):
        """Called whenever the search box text changes"""
        search_text = self.search_var.get()
        self.update_search_results(search_text)
    
    def update_search_results(self, search_text):
        """Update the listbox with records matching the search text"""
        self.results_listbox.delete(0, tk.END)
        self.matched_records = []
        
        if not search_text or not self.student_records:
            return
        
        # Case-insensitive substring match in student_name
        pattern = re.compile(re.escape(search_text), re.IGNORECASE)
        
        # Find matching records
        for record in self.student_records:
            name = record["student_name"]
            if pattern.search(name):
                self.matched_records.append(record)
        
        # Sort matches by name
        self.matched_records.sort(key=lambda x: x["student_name"])
        
        # Populate listbox
        for record in self.matched_records:
            display_text = f"{record['student_name']}"
            self.results_listbox.insert(tk.END, display_text)
    
    def on_select_student(self, event):
        """Show details for the selected student from the listbox"""
        selection = self.results_listbox.curselection()
        if not selection or not self.matched_records:
            return
        
        index = selection[0]
        if index < len(self.matched_records):
            student = self.matched_records[index]
            self.display_student_details(student)
    
    def display_student_details(self, student):
        """Format and display student details in the text area"""
        # Format details with consistent spacing
        details = f"""Name: {student['student_name']}
ID: {student['student_id']}
Class: {student['course']} {student['course_number']}
Section: {student['section']}
Level: {student['class_level']}
Email: {student['email']}
Source: {student['source_file']}
"""
        self.update_details_text(details)
    
    def update_details_text(self, text):
        """Update the details text widget with new content"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, text)
        self.details_text.config(state=tk.DISABLED)
    
    def update_status_bar(self):
        """Update status bar with current app state"""
        if not self.student_records:
            self.status_var.set("No rosters loaded")
        else:
            self.status_var.set(
                f"Loaded {len(self.loaded_files)} roster(s) with "
                f"{len(self.student_records)} student records"
            )
    
    def show_loaded_files(self):
        """Display a dialog showing currently loaded files"""
        if not self.loaded_files:
            messagebox.showinfo("Loaded Files", "No files are currently loaded.")
            return
        
        files_text = "Currently loaded roster files:\n\n"
        for i, file_path in enumerate(self.loaded_files, 1):
            files_text += f"{i}. {os.path.basename(file_path)}\n"
        
        messagebox.showinfo("Loaded Files", files_text)
    
    def show_about(self):
        """Show about dialog with app information"""
        about_text = f"""Student Lookup v{APP_VERSION}

A simple application to search and manage student rosters.

Features:
• Load up to 9 CSV roster files
• Quick student name search
• View detailed student information
• Persistence between sessions

Created with Python and Tkinter
"""
        messagebox.showinfo("About Student Lookup", about_text)
    
    def load_config(self):
        """Load previously used file paths from config"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.loaded_files = data.get("roster_files", [])
                    # Filter out files that no longer exist
                    self.loaded_files = [f for f in self.loaded_files if os.path.exists(f)]
        except Exception as e:
            print(f"Error loading config: {e}")
            self.loaded_files = []
    
    def save_config(self):
        """Save the current list of file paths to config"""
        try:
            # Ensure only existing files are saved
            valid_files = [f for f in self.loaded_files if os.path.exists(f)]
            data = {"roster_files": valid_files}
            
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

def main():
    app = StudentLookupApp()
    app.mainloop()

if __name__ == "__main__":
    main()