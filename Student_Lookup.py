import tkinter as tk
from tkinter import filedialog, messagebox
import os
import csv
import json
import re

CONFIG_FILE = "config.json"

class StudentLookupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Student Lookup")
        self.geometry("600x400")
        
        # Data structures
        self.loaded_files = []       # List of file paths loaded
        self.student_records = []    # List of dictionaries, each representing a student
        
        # Load config if it exists
        self.load_config()
        
        # Build GUI
        self.create_widgets()
        
        # If config exists, auto-load the saved CSVs
        if self.loaded_files:
            self.load_rosters_from_files(self.loaded_files)
    
    def create_widgets(self):
        """Create and pack the various widgets."""
        
        # Frame for top buttons
        top_frame = tk.Frame(self)
        top_frame.pack(pady=5)
        
        # Load rosters button
        load_button = tk.Button(top_frame, text="Load Rosters", command=self.on_load_rosters)
        load_button.pack(side=tk.LEFT, padx=5)
        
        # Flush data button
        flush_button = tk.Button(top_frame, text="Flush Data", command=self.on_flush_data)
        flush_button.pack(side=tk.LEFT, padx=5)
        
        # Frame for search box
        search_frame = tk.Frame(self)
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="Search Student Name:").pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)  # Trigger search as user types
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        # Frame for results list
        results_frame = tk.Frame(self)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_listbox = tk.Listbox(results_frame, height=10)
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_listbox.bind("<<ListboxSelect>>", self.on_select_student)
        
        # Scrollbar for the listbox
        scrollbar = tk.Scrollbar(results_frame, orient="vertical", command=self.results_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.config(yscrollcommand=scrollbar.set)
        
        # Frame for selected student info
        info_frame = tk.Frame(self, bd=2, relief=tk.GROOVE, padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_label = tk.Label(info_frame, text="Selected Student Details Will Appear Here")
        self.info_label.pack()
    
    def on_load_rosters(self):
        """Open a file dialog and load up to 9 CSV files."""
        file_paths = filedialog.askopenfilenames(
            title="Select up to 9 roster CSV files",
            filetypes=[("CSV Files", "*.csv")],
        )
        
        if not file_paths:
            return
        
        if len(file_paths) > 9:
            messagebox.showerror("Error", "You can load up to 9 rosters at once.")
            return
        
        # Store the new file paths
        self.loaded_files = list(file_paths)
        
        # Load rosters from these files
        self.load_rosters_from_files(self.loaded_files)
        
        # Save config
        self.save_config()
    
    def load_rosters_from_files(self, file_paths):
        """Load student data from the given CSV files."""
        # Clear existing records
        self.student_records.clear()
        
        for file_path in file_paths:
            # Parse course, number, section from filename
            filename = os.path.basename(file_path)  # e.g., "SOC-1101-W01.csv"
            
            # Split on ".csv" to remove extension, then split by '-'
            name_parts = filename.split(".csv")[0].split("-")
            if len(name_parts) < 3:
                # If the filename doesn't match the pattern, skip
                continue
            course = name_parts[0]
            course_number = name_parts[1]
            section = name_parts[2]
            
            # Read CSV rows
            with open(file_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Expecting columns: "Student Name", "Student ID", "Class Level", "Preferred Email"
                    student_name = row.get("Student Name", "").strip()
                    student_id = row.get("Student ID", "").strip()
                    class_level = row.get("Class Level", "").strip()
                    preferred_email = row.get("Preferred Email", "").strip()
                    
                    record = {
                        "course": course,
                        "course_number": course_number,
                        "section": section,
                        "student_name": student_name,
                        "student_id": student_id,
                        "class_level": class_level,
                        "email": preferred_email,
                    }
                    self.student_records.append(record)
        
        # After loading new data, clear search results
        self.update_search_results("")
        self.info_label.config(text="Rosters Loaded. Search for a student above.")
    
    def on_flush_data(self):
        """Remove all rosters and clear the config."""
        if messagebox.askyesno("Confirm", "Are you sure you want to flush all data?"):
            self.loaded_files = []
            self.student_records.clear()
            self.update_search_results("")
            self.info_label.config(text="All data flushed.")
            # Remove config file if it exists
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
    
    def on_search_change(self, *args):
        """Called whenever the search box text changes."""
        search_text = self.search_var.get()
        self.update_search_results(search_text)
    
    def update_search_results(self, search_text):
        """Update the listbox with records matching the search text."""
        self.results_listbox.delete(0, tk.END)
        
        if not search_text:
            return
        
        # Simple case-insensitive substring match in student_name
        pattern = re.compile(re.escape(search_text), re.IGNORECASE)
        
        self.matched_records = []  # keep a list of matched records
        for record in self.student_records:
            name = record["student_name"]
            if pattern.search(name):
                self.matched_records.append(record)
        
        # Populate listbox
        for i, record in enumerate(self.matched_records):
            self.results_listbox.insert(tk.END, record["student_name"])
    
    def on_select_student(self, event):
        """Show details for the selected student from the listbox."""
        selection = self.results_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        student = self.matched_records[index]
        
        details = (
            f"Name: {student['student_name']}\n"
            f"Class: {student['course']} {student['course_number']}\n"
            f"Section: {student['section']}\n"
            f"Email: {student['email']}"
        )
        self.info_label.config(text=details)
    
    def load_config(self):
        """Load previously used file paths from a JSON config, if available."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.loaded_files = data.get("roster_files", [])
    
    def save_config(self):
        """Save the current list of file paths to config."""
        data = {"roster_files": self.loaded_files}
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

def main():
    app = StudentLookupApp()
    app.mainloop()

if __name__ == "__main__":
    main()
