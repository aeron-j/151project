import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import re
import csv
import tkinter.simpledialog as simpledialog

CSV_FILE = os.path.join(os.path.dirname(__file__), 'student_data.csv')
COLLEGE_CSV = os.path.join(os.path.dirname(__file__), 'colleges.csv')
COURSE_CSV = os.path.join(os.path.dirname(__file__), 'courses.csv')

window = tk.Tk()
window.geometry("1250x500")
window.title("Student Data")

college_courses = {}
all_students = []
displayed_students = all_students.copy() #

def load_college_courses_from_csv():
    global college_courses
    college_courses.clear()
    college_courses["_orphaned_"] = []  # Ensure orphaned list exists
    
    try:
        # Load colleges
        if os.path.exists(COLLEGE_CSV):
            with open(COLLEGE_CSV, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                for row in reader:
                    if row and len(row) >= 2:
                        code = row[0]
                        name = row[1]
                        college_key = f"{code} - {name}"
                        college_courses[college_key] = []

        # Load courses - PROPERLY handle orphaned courses
        if os.path.exists(COURSE_CSV):
            with open(COURSE_CSV, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                for row in reader:
                    if row and len(row) >= 3:
                        course_code = row[0]
                        course_name = row[1]
                        college_code = row[2]
                        
                        course_entry = f"{course_code} - {course_name}"
                        
                        if college_code == "N/A":
                            college_courses["_orphaned_"].append(course_entry)
                        else:
                            college_key = next(
                                (k for k in college_courses if k.startswith(f"{college_code} -")),
                                None
                            )
                            if college_key:
                                college_courses[college_key].append(course_entry)
                            else:
                                college_courses["_orphaned_"].append(course_entry)
    except Exception as e:
        print(f"Error loading data: {e}")
        messagebox.showerror("Error", f"Failed to load college and course data: {str(e)}")

    return college_courses



def load_students_from_csv():
    global all_students
    all_students.clear()

    try:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  
                for row in reader:
                    if row and len(row) >= 8:  
                        all_students.append(tuple(row))
    except Exception as e:
        print(f"Error loading student data: {e}")
        messagebox.showerror("Error", f"Failed to load student data: {str(e)}")

    return all_students


def initialize_data():
    load_college_courses_from_csv()
    load_students_from_csv()


def save_students_to_csv():
    try:
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "First Name", "Last Name", "Email", "Phone", "Year Level", "College", "Course"])
            writer.writerows(all_students)
    except Exception as e:
        print(f"Error saving student data: {e}")
        messagebox.showerror("Error", f"Failed to save student data: {str(e)}")


class ValidationUtils:
    @staticmethod
    def create_validated_entry(parent, validate_type="text", **kwargs):
        entry = tk.Entry(parent, **kwargs)

        if validate_type == "text":
            def validate_text(P):
                return all(not c.isdigit() for c in P)
            vcmd = (parent.register(validate_text), '%P')  
            entry.config(validate="key", validatecommand=vcmd)

        elif validate_type == "code":
            def validate_code(P):
                allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-")
                return all(c in allowed_chars for c in P)
            vcmd = (parent.register(validate_code), '%P')  
            entry.config(validate="key", validatecommand=vcmd)

        return entry

    @staticmethod
    def validate_code_format(code, type_name):
        if type_name == "Course":
            
            if not re.match(r'^[A-Z0-9\-]+$', code):
                messagebox.showerror("Invalid Format", 
                                     f"{type_name} code must contain only letters, numbers, and hyphens.")
                return False
        else:  
            if not code.isalpha():
                messagebox.showerror("Invalid Format", 
                                     f"{type_name} code must contain only letters.")
                return False
        return True

    @staticmethod
    def validate_text_only(text, field_name):
        if any(char.isdigit() for char in text):
            messagebox.showerror("Invalid Input", 
                                 f"{field_name} must not contain numbers.")
            return False
        return True

class CollegeManager:
    def __init__(self, main_window, student_table_ref=None):
        self.window = tk.Toplevel(main_window)
        self.window.title("College Management")
        self.window.geometry("600x500")
        self.window.config(bg="#800000")
        self.window.transient(main_window)
        self.window.grab_set()
        
        self.main_window = main_window
        self.student_table_ref = student_table_ref  
        
        
        global college_courses
        self.college_courses = college_courses
        
        
        self.sort_var = tk.StringVar(value="College Code")
        self.sort_order = tk.StringVar(value="Ascending")
        self.search_var = tk.StringVar()
        
        
        table_frame = tk.Frame(self.window, bg="#800000")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        
        tk.Label(table_frame, text="Colleges", bg="#800000", fg="white", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        
        self.columns = ("College Code", "College Name", "Number of Courses")
        self.college_table = ttk.Treeview(table_frame, columns=self.columns, show="headings", height=15)
        
        for col in self.columns:
            self.college_table.heading(col, text=col)
            self.college_table.column(col, width=150)
        
        self.college_table.pack(fill=tk.BOTH, expand=True)
        
        
        button_frame = tk.Frame(self.window, bg="#800000")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Add College", bg="#7d6a69", fg="white", 
                 command=self.add_college).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Edit College", bg="#7d6a69", fg="white", 
                 command=self.edit_college).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete College", bg="#7d6a69", fg="white", 
                 command=self.delete_college).pack(side=tk.LEFT, padx=5)
      
        
        
        search_frame = tk.Frame(self.window, bg="#800000")
        search_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(search_frame, text="Search:", 
                bg="#800000", fg="white").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_var.trace('w', self.on_search_change)
        
        
        sort_frame = tk.Frame(self.window, bg="#800000")
        sort_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(sort_frame, text="Sort by:", 
                bg="#800000", fg="white").pack(side=tk.LEFT, padx=5)
        sort_options = ttk.Combobox(sort_frame, 
                                  textvariable=self.sort_var,
                                  values=["College Code", "College Name", "Number of Courses"],
                                  state='readonly',
                                  width=15)
        sort_options.pack(side=tk.LEFT, padx=5)
        
        order_options = ttk.Combobox(sort_frame, 
                                   textvariable=self.sort_order,
                                   values=["Ascending", "Descending"],
                                   state='readonly',
                                   width=10)
        order_options.pack(side=tk.LEFT, padx=5)
        
        tk.Button(sort_frame, text="Apply Sort", 
                 bg="#7d6a69", fg="white",
                 command=self.apply_sort).pack(side=tk.LEFT, padx=5)
        
        
        self.college_table.bind("<Button-1>", self.on_click)
        self._last_selected = None
        
        
        self.refresh_table()
        
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.window.destroy()

    def on_click(self, event):
        region = self.college_table.identify("region", event.x, event.y)
        if region != "cell":
            return
            
        item = self.college_table.identify_row(event.y)
        if not item:
            return
            
        if item == self._last_selected:
            self.college_table.selection_remove(item)
            self._last_selected = None
        else:
            self._last_selected = item

    def on_search_change(self, *args):
        self.refresh_table()

    def apply_sort(self):
        self.refresh_table()

    def refresh_table(self):
        self.college_table.delete(*self.college_table.get_children())
        
        try:
            
            colleges = []
            for college_key in self.college_courses.keys():
                parts = college_key.split(' - ', 1)
                if len(parts) == 2:
                    code, name = parts
                    num_courses = len(self.college_courses[college_key])
                    colleges.append((code, name, num_courses))

            search_text = self.search_var.get().lower()
            if search_text:
                colleges = [c for c in colleges if 
                          search_text in c[0].lower() or 
                          search_text in c[1].lower()]
        
            sort_by = self.sort_var.get()
            reverse = self.sort_order.get() == "Descending"
            
            if sort_by == "College Code":
                colleges.sort(key=lambda x: x[0], reverse=reverse)
            elif sort_by == "College Name":
                colleges.sort(key=lambda x: x[1], reverse=reverse)
            else:  
                colleges.sort(key=lambda x: x[2], reverse=reverse)
        
            for code, name, num_courses in colleges:
                self.college_table.insert("", "end", values=(code, name, num_courses))
                
        except Exception as e:
            print(f"Error refreshing college table: {e}")
            messagebox.showerror("Error", "Failed to refresh college table")

    def add_college(self):
        add_dialog = tk.Toplevel(self.window)
        add_dialog.title("Add New College")
        add_dialog.geometry("400x200")
        add_dialog.config(bg="#800000")
        add_dialog.transient(self.window)
        add_dialog.grab_set()
        
        tk.Label(add_dialog, text="College Code:", 
                bg="#800000", fg="white").pack(pady=5)
        code_entry = ValidationUtils.create_validated_entry(add_dialog, "code")
        code_entry.pack(pady=5)
        
        tk.Label(add_dialog, text="College Name:", 
                bg="#800000", fg="white").pack(pady=5)
        name_entry = ValidationUtils.create_validated_entry(add_dialog, "text",width=40)
        name_entry.pack(pady=5)
        
        def save():
            code = code_entry.get().strip().upper()
            name = name_entry.get().strip().title()
            
            if not all([code, name]):
                messagebox.showerror("Error", "All fields must be filled")
                return
                
            if not ValidationUtils.validate_code_format(code, "College"):
                return
                
            if not ValidationUtils.validate_text_only(name, "College name"):
                return
                
            if any(k.startswith(f"{code} -") for k in self.college_courses):
                messagebox.showerror("Duplicate", f"College with code {code} already exists")
                return

            
            if self.check_college_duplicate(name):
                messagebox.showerror("Duplicate", f"A college named '{name}' already exists.")
                return
                
            new_college = f"{code} - {name}"
            self.college_courses[new_college] = []
            
            
            global college_courses
            college_courses[new_college] = []
            
            
            if self.save_colleges_to_csv():
                load_college_courses_from_csv()
                self.college_courses = college_courses
                self.refresh_table()
                if 'student_filter_sort' in globals() and student_filter_sort:
                    student_filter_sort.refresh_filter_values()
                    student_filter_sort.apply_filters()
                add_dialog.destroy()
                
            
        tk.Button(add_dialog, text="Save", 
                bg="#7d6a69", fg="white",
                command=save).pack(pady=10)

    def edit_college(self):
        selected = self.college_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a college to edit.")
            return
            
        values = self.college_table.item(selected)['values']
        if len(values) < 2:
            messagebox.showerror("Error", "Invalid selection data")
            return

        current_code, current_name = values[0], values[1]
        old_college = f"{current_code} - {current_name}"  
        
        edit_dialog = tk.Toplevel(self.window)
        edit_dialog.title("Edit College")
        edit_dialog.geometry("400x200")
        edit_dialog.config(bg="#800000")
        edit_dialog.transient(self.window)
        edit_dialog.grab_set()
        
        tk.Label(edit_dialog, text="College Code:", 
                bg="#800000", fg="white").pack(pady=5)
        code_entry = ValidationUtils.create_validated_entry(edit_dialog, "code")
        code_entry.insert(0, current_code)
        code_entry.pack(pady=5)
        
        tk.Label(edit_dialog, text="College Name:", 
                bg="#800000", fg="white").pack(pady=5)
        name_entry = ValidationUtils.create_validated_entry(edit_dialog, "text", width=40)
        name_entry.insert(0, current_name)
        name_entry.pack(pady=5)
        
        def save():
            new_code = code_entry.get().strip().upper()
            new_name = name_entry.get().strip().title()
            new_college = f"{new_code} - {new_name}"

            if not all([new_code, new_name]):
                messagebox.showerror("Error", "All fields must be filled")
                return
                
            if not ValidationUtils.validate_code_format(new_code, "College"):
                return
                
            if not ValidationUtils.validate_text_only(new_name, "College name"):
                return
                
            if new_college != old_college:
                if any(k.startswith(f"{new_code} -") and k != old_college for k in self.college_courses):
                    messagebox.showerror("Duplicate", f"College with code {new_code} already exists")
                    return

                if self.check_college_duplicate(new_name, exclude_key=old_college):
                    messagebox.showerror("Duplicate", f"A college named '{new_name}' already exists.")
                    return

            # Update student records first
            self.update_student_records_college(old_college, new_college)
            
            # Then update the college in the courses structure
            if old_college in self.college_courses:
                courses = self.college_courses.pop(old_college, [])
                self.college_courses[new_college] = courses
                
            # Save changes
            self.save_colleges_to_csv()
            save_students_to_csv()
            
            # Refresh displays
            load_college_courses_from_csv()
            self.college_courses = college_courses
            self.refresh_table()
            if self.student_table_ref:
                self.student_table_ref.refresh_table()

            if 'student_filter_sort' in globals() and student_filter_sort:
                student_filter_sort.refresh_filter_values()
                student_filter_sort.apply_filters()
            
            edit_dialog.destroy()
            
        tk.Button(edit_dialog, text="Save Changes", 
                 bg="#7d6a69", fg="white",
                 command=save).pack(pady=10)

    def update_student_records_college(self, old_college, new_college):
        global all_students
        
        # Get both full name and code versions for matching
        old_college_code = old_college.split(' - ')[0] if ' - ' in old_college else old_college
        new_college_code = new_college.split(' - ')[0] if ' - ' in new_college else new_college
        new_college_name = new_college.split(' - ')[1] if ' - ' in new_college else ""
        
        for i in range(len(all_students)):
            student_list = list(all_students[i])
            if len(student_list) >= 7:
                student_college = student_list[6]
                
                # Check both full college name and just the code
                if (student_college == old_college or 
                    (isinstance(student_college, str) and 
                    (student_college.startswith(old_college_code + ' -') or 
                    student_college == old_college_code))):
                    
                    # Update to full college name if available, otherwise just code
                    if new_college_name:
                        student_list[6] = f"{new_college_code} - {new_college_name}"
                    else:
                        student_list[6] = new_college_code
                    
                    all_students[i] = tuple(student_list)
        
        save_students_to_csv()

    def delete_college(self):
        global college_courses, all_students

        selected = self.college_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a college to delete.")
            return

        values = self.college_table.item(selected)['values']
        if len(values) < 2:
            messagebox.showerror("Error", "Invalid selection data")
            return

        college_code, college_name = values[0], values[1]
        college_key = f"{college_code} - {college_name}"

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete college '{college_key}'?\nCourses will remain, but students will be marked with N/A in College."):
            # Remove the college
            deleted_courses = self.college_courses.pop(college_key, [])
            if college_key in college_courses:
                del college_courses[college_key]

            # Update students: set college = "N/A", leave course untouched
            updated_students = []
            for student in all_students:
                student_list = list(student)
                if len(student_list) >= 7 and student_list[6] == college_key:
                    student_list[6] = "N/A"
                updated_students.append(tuple(student_list))
            all_students = updated_students

            self.save_colleges_to_csv()
            save_students_to_csv()
            load_college_courses_from_csv()
            self.college_courses = college_courses
            self.refresh_table()

            if self.student_table_ref:
                self.student_table_ref.refresh_table()
            if 'student_filter_sort' in globals() and student_filter_sort:
                student_filter_sort.refresh_filter_values()

            messagebox.showinfo("College Deleted", f"College '{college_key}' has been deleted.\nCourses were retained.")



    def update_student_courses_college(self, affected_courses, old_college, new_college):
        global all_students
        updated_students = []
        any_updated = False
        
        for student in all_students:
            student_list = list(student)
            if len(student_list) >= 7 and student_list[6] == old_college:
                student_list[6] = new_college
                any_updated = True
            
            if len(student_list) >= 8 and student_list[7] in affected_courses:
                if student_list[6] == old_college:  
                    student_list[6] = new_college
                    any_updated = True
                    
            updated_students.append(tuple(student_list))
        
        if any_updated:
            all_students = updated_students
            save_students_to_csv()  

    def check_college_duplicate(self, name, exclude_key=None):
        normalized_name = name.strip().lower()

        for college_key in self.college_courses:
            if college_key == exclude_key:
                continue

            parts = college_key.split(' - ', 1)
            if len(parts) == 2:
                existing_name = parts[1].strip().lower()
                if existing_name == normalized_name:
                    return True

        return False
    
    def save_colleges_to_csv(self):
        try:
            colleges_to_save = []
            for college_key in self.college_courses:
                parts = college_key.split(' - ', 1)
                if len(parts) == 2:
                    code, name = parts
                    colleges_to_save.append([code, name])
            
            with open(COLLEGE_CSV, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Code", "Name"])  
                for college in colleges_to_save:
                    writer.writerow(college)
            
            self.save_courses_to_csv()
            
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save colleges: {str(e)}")
            return False
    
    def save_courses_to_csv(self):
        try:
            courses_to_save = []
            for college_key, course_list in self.college_courses.items():
                college_code = college_key.split(' - ', 1)[0]
                for course_entry in course_list:
                    course_parts = course_entry.split(' - ', 1)
                    if len(course_parts) == 2:
                        course_code, course_name = course_parts
                        courses_to_save.append([course_code, course_name, college_code])

            # Add orphaned courses from student data that are no longer linked to a college
            known_courses = set(f"{c[0]} - {c[1]}" for c in courses_to_save)
            used_courses = set(s[7] for s in all_students if len(s) >= 8)
            orphaned_courses = used_courses - known_courses

            for orphan in orphaned_courses:
                if ' - ' in orphan:
                    course_code, course_name = orphan.split(' - ', 1)
                    courses_to_save.append([course_code, course_name, "N/A"])

            with open(COURSE_CSV, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Course Code", "Course Name", "College Code"])
                writer.writerows(courses_to_save)

            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save courses: {str(e)}")
            return False

class CourseManager:
    def __init__(self, main_window, college_courses, college_manager_ref=None, student_table_ref=None):
        self.window = tk.Toplevel(main_window)
        self.window.title("Course Management")
        self.window.geometry("800x500")
        self.window.config(bg="#800000")
        self.window.transient(main_window)
        self.window.grab_set()

        self.college_courses = college_courses
        self.college_manager_ref = college_manager_ref
        self.student_table_ref = student_table_ref

        self.sort_var = tk.StringVar(value="Course Code")
        self.sort_order = tk.StringVar(value="Ascending")
        self.search_var = tk.StringVar()
        self.college_filter_var = tk.StringVar(value="All Colleges")

        main_frame = tk.Frame(self.window, bg="#800000")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        filter_frame = tk.Frame(main_frame, bg="#800000")
        filter_frame.pack(fill=tk.X, pady=5)

        tk.Label(filter_frame, text="Filter by College:", bg="#800000", fg="white").pack(side=tk.LEFT, padx=5)
        college_options = ["All Colleges"] + [k for k in self.college_courses if k != "_orphaned_"]
        self.college_filter = ttk.Combobox(filter_frame, textvariable=self.college_filter_var,
                                           values=college_options, state='readonly', width=30)
        self.college_filter['values'] = ["All Colleges"] + [k for k in self.college_courses if k != "_orphaned_"]
        self.college_filter.pack(side=tk.LEFT, padx=5)

        tk.Button(filter_frame, text="Apply Filter", bg="#7d6a69", fg="white",
                  command=self.refresh_table).pack(side=tk.LEFT, padx=5)

        self.columns = ("Course Code", "Course Name", "College")
        self.course_table = ttk.Treeview(main_frame, columns=self.columns, show="headings")
        for col in self.columns:
            self.course_table.heading(col, text=col)
            if col == "Course Name":
                self.course_table.column(col, width=300)
            else:
                self.course_table.column(col, width=150)
        self.course_table.pack(fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(main_frame, bg="#800000")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Course", bg="#7d6a69", fg="white",
                  command=self.add_course).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Edit Course", bg="#7d6a69", fg="white",
                  command=self.edit_course).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Course", bg="#7d6a69", fg="white",
                  command=self.delete_course).pack(side=tk.LEFT, padx=5)

        search_frame = tk.Frame(main_frame, bg="#800000")
        search_frame.pack(fill=tk.X, pady=5)

        tk.Label(search_frame, text="Search:", bg="#800000", fg="white").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_by_var = tk.StringVar(value="Course Code")
        search_by_options = ttk.Combobox(search_frame, textvariable=self.search_by_var,
                                        values=["Course Code", "Course Name"],
                                        state='readonly', width=15)
        search_by_options.pack(side=tk.LEFT, padx=5)

        self.search_var.trace('w', self.on_search_change)

        sort_frame = tk.Frame(main_frame, bg="#800000")
        sort_frame.pack(fill=tk.X, pady=5)

        tk.Label(sort_frame, text="Sort by:", bg="#800000", fg="white").pack(side=tk.LEFT, padx=5)
        sort_options = ttk.Combobox(sort_frame, textvariable=self.sort_var,
                                    values=["Course Code", "Course Name", "College"],
                                    state='readonly', width=15)
        sort_options.pack(side=tk.LEFT, padx=5)

        order_options = ttk.Combobox(sort_frame, textvariable=self.sort_order,
                                     values=["Ascending", "Descending"],
                                     state='readonly', width=10)
        order_options.pack(side=tk.LEFT, padx=5)

        tk.Button(sort_frame, text="Apply Sort", bg="#7d6a69", fg="white",
                  command=self.apply_sort).pack(side=tk.LEFT, padx=5)

        self.course_table.bind("<Button-1>", self.on_click)
        self._last_selected = None

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.refresh_table()

    def on_close(self):
        if self.college_manager_ref:
            self.college_manager_ref.refresh_table()
        self.window.destroy()

    def on_click(self, event):
        region = self.course_table.identify("region", event.x, event.y)
        if region != "cell":
            return
        item = self.course_table.identify_row(event.y)
        if not item:
            return
        if item == self._last_selected:
            self.course_table.selection_remove(item)
            self._last_selected = None
        else:
            self._last_selected = item

    def on_search_change(self, *args):
        self.refresh_table()

    def apply_sort(self):
        self.refresh_table()

    def refresh_table(self):
        self.course_table.delete(*self.course_table.get_children())
        try:
            courses = []
            
            # Process all colleges including orphaned courses
            for college_key, course_list in self.college_courses.items():
                for course in course_list:
                    parts = course.split(" - ", 1)
                    if len(parts) == 2:
                        code, name = parts
                        # For orphaned courses, show "N/A" as college
                        if college_key == "_orphaned_":
                            courses.append((code, name, "N/A"))
                        else:
                            # For normal courses, show the college code
                            college_code = college_key.split(" - ")[0]
                            courses.append((code, name, college_code))

            # Apply search if any
            search_text = self.search_var.get().lower()
            search_by = self.search_by_var.get()

            if search_text:
                if search_by == "Course Code":
                    courses = [c for c in courses if search_text in c[0].lower()]
                elif search_by == "Course Name":
                    courses = [c for c in courses if search_text in c[1].lower()]

            # Apply sorting
            sort_by = self.sort_var.get()
            reverse = self.sort_order.get() == "Descending"
            if sort_by == "Course Code":
                courses.sort(key=lambda x: x[0], reverse=reverse)
            elif sort_by == "Course Name":
                courses.sort(key=lambda x: x[1], reverse=reverse)
            else:
                courses.sort(key=lambda x: x[2], reverse=reverse)

            # Display all courses
            for code, name, college in courses:
                self.course_table.insert("", "end", values=(code, name, college))

        except Exception as e:
            print(f"Error refreshing course table: {e}")
            messagebox.showerror("Error", "Failed to refresh course table")


    def add_course(self):
        add_dialog = tk.Toplevel(self.window)
        add_dialog.title("Add New Course")
        add_dialog.geometry("500x250")
        add_dialog.config(bg="#800000")
        add_dialog.transient(self.window)
        add_dialog.grab_set()
        
        tk.Label(add_dialog, text="Course Code:", 
                bg="#800000", fg="white").pack(pady=5)
        code_entry = ValidationUtils.create_validated_entry(add_dialog, "code")
        code_entry.pack(pady=5)
        
        tk.Label(add_dialog, text="Course Name:", 
                bg="#800000", fg="white").pack(pady=5)
        name_entry = ValidationUtils.create_validated_entry(add_dialog, "text", width=40)
        name_entry.pack(pady=5)
        
        tk.Label(add_dialog, text="Select College:", 
                bg="#800000", fg="white").pack(pady=5)
        
        college_var = tk.StringVar(value="")  
        valid_colleges = [k for k in self.college_courses if k != "_orphaned_"]
        college_dropdown = ttk.Combobox(add_dialog, 
            textvariable=college_var,
            values=[""] + valid_colleges,  
                                    state='readonly',
                                    width=40)
        college_dropdown.pack(pady=5)
        
        if self.college_filter_var.get() != "All Colleges":
            college_var.set(self.college_filter_var.get())
        
        def save():
            code = code_entry.get().strip().upper()
            name = name_entry.get().strip().title()
            college = college_var.get()
            
            if not all([code, name, college]):
                messagebox.showerror("Error", "All fields must be filled")
                return
                
            if not ValidationUtils.validate_code_format(code, "Course"):
                return
                
            if not ValidationUtils.validate_text_only(name, "Course name"):
                return
                
            if self.check_course_duplicate(code, college, name):
                return
            
            new_course = f"{code} - {name}"
            self.college_courses[college].append(new_course)
            self.save_to_csv()
            if 'student_filter_sort' in globals() and student_filter_sort:
                    student_filter_sort.apply_filters()
            
            self.refresh_table()
            add_dialog.destroy()
            
        tk.Button(add_dialog, text="Save", 
                bg="#7d6a69", fg="white",
                command=save).pack(pady=10)

    def edit_course(self):
        selected = self.course_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a course to edit.")
            return
            
        values = self.course_table.item(selected)['values']
        if len(values) < 3:
            messagebox.showerror("Error", "Invalid selection data")
            return

        current_code, current_name, current_college = values
        old_course = f"{current_code} - {current_name}"
        
        if current_college == "N/A":
            full_college_key = "_orphaned_"
        else:
            full_college_key = next((k for k in self.college_courses if k.startswith(f"{current_college} -")), None)
            if not full_college_key:
                messagebox.showerror("Error", f"College with code {current_college} not found")
                return
        
        edit_dialog = tk.Toplevel(self.window)
        edit_dialog.title("Edit Course")
        edit_dialog.geometry("500x250")
        edit_dialog.config(bg="#800000")
        edit_dialog.transient(self.window)
        edit_dialog.grab_set()
        
    
        tk.Label(edit_dialog, text="Course Code:", 
                bg="#800000", fg="white").pack(pady=5)
        code_entry = ValidationUtils.create_validated_entry(edit_dialog, "code")
        code_entry.insert(0, current_code)
        code_entry.pack(pady=5)
        
        tk.Label(edit_dialog, text="Course Name:", 
                bg="#800000", fg="white").pack(pady=5)
        name_entry = ValidationUtils.create_validated_entry(edit_dialog, "text", width=40)
        name_entry.insert(0, current_name)
        name_entry.pack(pady=5)
        
        
        tk.Label(edit_dialog, text="Select College:", 
                bg="#800000", fg="white").pack(pady=5)
        
        college_var = tk.StringVar(value=full_college_key)
        valid_colleges = [k for k in self.college_courses if k != "_orphaned_"]
        college_dropdown = ttk.Combobox(edit_dialog, 
            textvariable=college_var,
            values=valid_colleges,
                                    state='readonly',
                                    width=40)
        college_dropdown.pack(pady=5)
        
        def save():
            new_code = code_entry.get().strip().upper()
            new_name = name_entry.get().strip().title()
            new_college = college_var.get()
            
            if not all([new_code, new_name, new_college]):
                messagebox.showerror("Error", "All fields must be filled")
                return
                
            if not ValidationUtils.validate_code_format(new_code, "Course"):
                return
                
            if not ValidationUtils.validate_text_only(new_name, "Course name"):
                return
            
            new_course = f"{new_code} - {new_name}"
            
            if new_course != old_course:
                if self.check_course_duplicate(new_code, new_college, new_name, exclude_course=old_course):
                    return

            # Get college codes for updating student records
            old_college_code = full_college_key.split(' - ')[0] if ' - ' in full_college_key else full_college_key
            new_college_code = new_college.split(' - ')[0] if ' - ' in new_college else new_college
            
            # Update course in college structure
            if old_course in self.college_courses[full_college_key]:
                self.college_courses[full_college_key].remove(old_course)
                
            self.college_courses[new_college].append(new_course)
            
            # Update student records with both new course and college info
            self.update_student_records_course(old_course, new_course, old_college_code, new_college_code)
            
            # Save changes
            self.save_to_csv()
            save_students_to_csv()
            
            # Refresh displays
            self.refresh_table()
            if self.student_table_ref:
                self.student_table_ref.refresh_table()

            if 'student_filter_sort' in globals() and student_filter_sort:
                student_filter_sort.refresh_filter_values()
                student_filter_sort.apply_filters()
            
            edit_dialog.destroy()
            
        tk.Button(edit_dialog, text="Save Changes", 
                bg="#7d6a69", fg="white",
                command=save).pack(pady=10)

    def update_student_records_course(self, old_course, new_course, old_college_code, new_college_code):
        global all_students
        updated_students = []
        
        # Extract old course code safely
        old_course_code = old_course.split(' - ')[0] if isinstance(old_course, str) and ' - ' in old_course else old_course
        
        for student in all_students:
            if not student or len(student) < 8:  # Skip invalid records
                updated_students.append(student)
                continue
                
            student_list = list(student)
            
            # Safely get student's course info
            student_course = student_list[7] if len(student_list) > 7 else ""
            student_course_code = student_course.split(' - ')[0] if isinstance(student_course, str) and ' - ' in student_course else student_course
            
            # Safely get student's college info
            student_college = student_list[6] if len(student_list) > 6 else ""
            student_college_code = student_college.split(' - ')[0] if isinstance(student_college, str) and ' - ' in student_college else student_college
            
            # Check if this record needs updating
            needs_update = (
                student_course == old_course or 
                student_course_code == old_course_code or
                student_course_code == old_course  # Handle case where old_course might be just a code
            )
            
            if needs_update:
                # Update course to new full name
                student_list[7] = new_course if isinstance(new_course, str) else ""
                
                # Update college if it matches the old college code
                if student_college_code == old_college_code:
                    if isinstance(new_college_code, str):
                        # Find the full college name in college_courses
                        full_college_name = next(
                            (college for college in self.college_courses 
                            if college.startswith(f"{new_college_code} - ")),
                            new_college_code  # Fallback to just code if not found
                        )
                        student_list[6] = full_college_name
                    
            updated_students.append(tuple(student_list))
        
        all_students = updated_students
        save_students_to_csv()

    def delete_course(self):
        selected = self.course_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a course to delete.")
            return

        values = self.course_table.item(selected)['values']
        if len(values) < 3:
            messagebox.showerror("Error", "Invalid selection data")
            return

        course_code, course_name, college_code = values
        course_full = f"{course_code} - {course_name}"
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {course_full}?"):
            return

        # 1. Remove from memory structure
        if college_code == "N/A":
            if "_orphaned_" in self.college_courses and course_full in self.college_courses["_orphaned_"]:
                self.college_courses["_orphaned_"].remove(course_full)
        else:
            college_key = next((k for k in self.college_courses if k.startswith(f"{college_code} -")), None)
            if college_key and course_full in self.college_courses.get(college_key, []):
                self.college_courses[college_key].remove(course_full)

        # 2. Update student records that reference this course
        global all_students
        updated_students = []
        for student in all_students:
            if len(student) > 7 and student[7] == course_full:
                student = list(student)
                student[7] = "N/A"  # Reset course to N/A
                if len(student) > 6 and student[6] == college_code:
                    student[6] = "N/A"  # Reset college if it matches
                student = tuple(student)
            updated_students.append(student)
        all_students = updated_students

        # 3. Save changes to both files
        try:
            # Save course changes
            with open(COURSE_CSV, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Course Code", "Course Name", "College Code"])
                for college_key, courses in self.college_courses.items():
                    college_code = "N/A" if college_key == "_orphaned_" else college_key.split(' - ')[0]
                    for course in courses:
                        parts = course.split(' - ', 1)
                        if len(parts) == 2:
                            writer.writerow([parts[0], parts[1], college_code])
            
            # Save student changes
            save_students_to_csv()

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save changes: {str(e)}")
            return

        # 4. Refresh displays
        self.refresh_table()
        if self.student_table_ref:
            self.student_table_ref.refresh_table()
        
        messagebox.showinfo("Success", f"Course {course_full} deleted successfully")



    def check_course_duplicate(self, code, college, name=None, exclude_course=None):
        normalized_code = code.strip().upper()
        normalized_name = name.strip().lower() if name else None

        for college_key, course_list in self.college_courses.items():
            for course in course_list:
                if exclude_course and course == exclude_course:
                    continue

                parts = course.split(' - ', 1)
                if len(parts) != 2:
                    continue

                existing_code = parts[0].strip().upper()
                existing_name = parts[1].strip().lower()

                if normalized_code == existing_code:
                    messagebox.showerror("Duplicate", f"Course code '{code}' already exists in another college!")
                    return True

                if normalized_name and normalized_name == existing_name:
                    messagebox.showerror("Duplicate", f"Course name '{name}' already exists in another college!")
                    return True

        return False


    def save_to_csv(self):
        try:
            with open(COURSE_CSV, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Course Code", "Course Name", "College Code"])
                
                # Save all courses including orphaned ones
                for college_key, courses in self.college_courses.items():
                    college_code = "N/A" if college_key == "_orphaned_" else college_key.split(' - ')[0]
                    for course in courses:
                        parts = course.split(' - ', 1)
                        if len(parts) == 2:
                            code, name = parts
                            writer.writerow([code, name, college_code])
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save courses: {str(e)}")


def is_duplicate_id(idno, current_item=None):
    if current_item:
        current_id = table.item(current_item)['values'][0]
        if idno == current_id:  
            return False
    
    for item in table.get_children():
        if current_item and item == current_item: 
            continue
        if table.item(item)['values'][0] == idno:  
            return True
    return False


def refresh_table(students_to_display=None):
    global all_students, current_page, total_pages

    if students_to_display is None:
        students_to_display = get_filtered_students()

    table.delete(*table.get_children())

    total_pages = max(1, (len(students_to_display) + rows_per_page - 1) // rows_per_page)
    current_page = min(current_page, total_pages)

    start_idx = (current_page - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, len(students_to_display))

    for student in students_to_display[start_idx:end_idx]:
        display_values = list(student)
        if ' - ' in str(student[6]):
            display_values[6] = student[6].split(' - ')[0]
        if ' - ' in str(student[7]):
            display_values[7] = student[7].split(' - ')[0]
        table.insert("", "end", values=display_values)

    page_info.config(text=f"Page {current_page} of {total_pages} | Total: {len(students_to_display)} students")

    btn_first.config(state="normal" if current_page > 1 else "disabled")
    btn_prev.config(state="normal" if current_page > 1 else "disabled")
    btn_next.config(state="normal" if current_page < total_pages else "disabled")
    btn_last.config(state="normal" if current_page < total_pages else "disabled")

    

def add_student():
    def save_student():
        global all_students
        student_idno = entry_idno.get()
        student_firstname = entry_firstname.get().upper()
        student_lastname = entry_lastname.get().upper()
        student_age = entry_age.get()
        student_gender = gender_var.get()
        student_yearlevel = yearlevel_var.get()
        selected_college = college_var.get()
        selected_course = course_var.get()
        
        if not all([student_firstname, student_lastname, student_age, student_gender, 
                   student_idno, student_yearlevel, selected_college, selected_course]):
            msg = messagebox.showwarning("Missing Input", "Please fill in all fields.", parent=new_window)
            return

        if is_duplicate_id(student_idno):
            messagebox.showwarning("Duplicate ID", "This ID number already exists.", parent=new_window)
            return

        if not re.match(r'^\d{4}-\d{4}$', student_idno):
            msg = messagebox.showwarning("Invalid ID#", "ID# must be in the format YYYY-NNNN.", parent=new_window)
            return
        
        college_code = selected_college.split(' - ')[0]
        course_code = selected_course.split(' - ')[0]
        
        new_student = (student_idno, student_firstname, student_lastname, 
                      student_age, student_gender, student_yearlevel, 
                      college_code,  
                      course_code)   
        
        all_students.append(new_student)
        refresh_table()
        save_to_csv()
        new_window.destroy()

    
    def validate_char(char):
        return char.isalpha() or char == "" or char == " "

    def validate_int(char):
        return char.isdigit() or char == ""

    def validate_idno(char):
        return re.match(r'^\d{0,4}(-\d{0,4})?$', char) is not None
    
    def update_courses(*args):
        selected_college = college_var.get()
        
        # Skip if no college selected or invalid
        if not selected_college or selected_college == "_orphaned_":
            course_dropdown['values'] = []
            course_var.set('')
            return
        
        # Get courses for selected college
        course_options = college_courses.get(selected_college, [])
        course_dropdown['values'] = course_options
        course_var.set('')

    college_options = []
    for college_key in college_courses.keys():
        if ' - ' in college_key:
            code, name = college_key.split(' - ')
            college_options.append(f"{code} - {name}")  
        else:
            college_options.append(college_key)

    new_window = tk.Toplevel(window)
    new_window.geometry("450x300")
    new_window.title("Add New Student")
    new_window.config(bg="#800000")
    
    new_window.transient(window)
    new_window.grab_set()

    vcmd_char = new_window.register(validate_char)
    vcmd_int = new_window.register(validate_int)
    vcmd_idno = new_window.register(validate_idno)
    
    label_idno = tk.Label(new_window, text="ID#:", bg="#800000", fg="white")
    label_idno.grid(row=1, column=0)
    label_idno = tk.Label(new_window, text="(ex. YYYY-NNNN)", bg="#800000", fg="white")
    label_idno.grid(row=1, column=2, sticky="w")
    entry_idno = tk.Entry(new_window, validate="key", validatecommand=(vcmd_idno, '%P'), width=40)
    entry_idno.grid(row=1, column=1, sticky="w")

    label_name = tk.Label(new_window, text="First Name:", bg="#800000", fg="white")
    label_name.grid(row=2, column=0)
    entry_firstname = tk.Entry(new_window, validate="key", validatecommand=(vcmd_char, '%S'), width=40)
    entry_firstname.grid(row=2, column=1, sticky="w")
    
    label_lastname = tk.Label(new_window, text="Last Name:", bg="#800000", fg="white")
    label_lastname.grid(row=3, column=0)
    entry_lastname = tk.Entry(new_window, validate="key", validatecommand=(vcmd_char, '%S'), width=40)
    entry_lastname.grid(row=3, column=1,sticky="w")
    
    label_age = tk.Label(new_window, text="Age:", bg="#800000", fg="white")
    label_age.grid(row=4, column=0)
    entry_age = tk.Entry(new_window, validate="key", validatecommand=(vcmd_int, '%S'))
    entry_age.grid(row=4, column=1, sticky="w")

    
    label_gender = tk.Label(new_window, text="Gender:", bg="#800000", fg="white")
    label_gender.grid(row=5, column=0)
    gender_var = tk.StringVar(new_window)
    gender_choices = ["Male", "Female", "Others"]
    gender_dropdown = ttk.Combobox(new_window, textvariable=gender_var, values=gender_choices, state='readonly', width=17)  # Increased width to show full names
    gender_dropdown.grid(row=5, column=1, sticky="w")

    
    label_yearlevel = tk.Label(new_window, text="Year Level:", bg="#800000", fg="white")
    label_yearlevel.grid(row=6, column=0)
    yearlevel_var = tk.StringVar(new_window)
    yearlevel_choices = ["1st", "2nd", "3rd", "4th", "5+"]
    yearlevel_dropdown = ttk.Combobox(new_window, textvariable=yearlevel_var, values=yearlevel_choices, state='readonly', width=17)  # Increased width to show full names
    yearlevel_dropdown.grid(row=6, column=1, sticky="w")

    
    label_college = tk.Label(new_window, text="College:", bg="#800000", fg="white")
    label_college.grid(row=7, column=0)
    college_var = tk.StringVar(new_window)
    college_options = [k for k in college_courses if k != "_orphaned_"]  # Orphaned courses excluded
    college_dropdown = ttk.Combobox(new_window, textvariable=college_var, values=college_options, state='readonly', width=40)  # Increased width to show full names
    college_dropdown.grid(row=7, column=1)
    college_dropdown.bind("<<ComboboxSelected>>", update_courses)

   
    label_course = tk.Label(new_window, text="Course:", bg="#800000", fg="white")
    label_course.grid(row=8, column=0)
    course_var = tk.StringVar(new_window)
    course_dropdown = ttk.Combobox(new_window, textvariable=course_var, values=[], state='readonly', width=40)  # Increased width to show full names
    course_dropdown.grid(row=8, column=1)

    button_save = tk.Button(new_window, text="Save", bg="#d9a300", command=save_student)
    button_save.grid(row=9, column=0, columnspan=2, pady=10)


def delete_student():
    global all_students
    selected_item = table.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a student to delete.")
        return

    confirm = messagebox.askyesno("Delete Confirmation", "Are you sure you want to delete this student?")
    if confirm:
        deleted_id = table.item(selected_item)['values'][0]
        
        
        all_students = [student for student in all_students if student[0] != deleted_id]
        
        save_to_csv()
        
        refresh_table()


def update_student():
    selected_item = table.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a student to update.")
        return
    
    current_values = table.item(selected_item)['values']
    
    def save_changes():
        global all_students
        student_idno = entry_idno.get()
        student_firstname = entry_firstname.get().upper()
        student_lastname = entry_lastname.get().upper()
        student_age = entry_age.get()
        student_gender = gender_var.get()
        student_yearlevel = yearlevel_var.get()
        selected_college = college_var.get()
        selected_course_abbr = course_var.get()

        if not all([student_firstname, student_lastname, student_age, student_gender, 
                   student_idno, student_yearlevel, selected_college, selected_course_abbr]):
            msg = messagebox.showwarning("Missing Input", "Please fill in all fields.", parent=update_window)
            return

        if is_duplicate_id(student_idno, selected_item):
            messagebox.showwarning("Duplicate ID", "This ID number already exists.", parent=update_window)
            return

        if not re.match(r'^\d{4}-\d{4}$', student_idno):
            msg = messagebox.showwarning("Invalid ID#", "ID# must be in the format YYYY-NNNN.", parent=update_window)
            return
        
        full_course_name = next((course for course in college_courses[selected_college] 
                               if course.startswith(selected_course_abbr)), "")
        
        
        updated_student = (student_idno, student_firstname, student_lastname, 
                          student_age, student_gender, student_yearlevel, 
                          selected_college, full_course_name)
        
        
        original_id = table.item(selected_item)['values'][0]
        
        
        for i, student in enumerate(all_students):
            if student[0] == original_id:  
                all_students[i] = updated_student
                break
        
       
        save_to_csv()
        
        refresh_table()
        
        update_window.destroy()

    
    def validate_char(current_value, inserted_char):
        return all(c.isalpha() or c.isspace() for c in current_value + inserted_char) or inserted_char == ""

    def validate_int(char):
        return char.isdigit() or char == ""

    def validate_idno(char):
        return re.match(r'^\d{0,4}(-\d{0,4})?$', char) is not None
    
    def update_courses(*args):
        selected_college = college_var.get()
        if not selected_college or selected_college == "_orphaned_":
            course_dropdown['values'] = []
            course_var.set('')
            return
        course_options = []
        
        for course in college_courses.get(selected_college, []):
            course_options.append(course)  
            
        course_options = college_courses.get(selected_college, [])
        course_dropdown['values'] = course_options
        course_var.set('')

    college_options = []
    for college_key in college_courses.keys():
        if ' - ' in college_key:
            code, name = college_key.split(' - ')
            college_options.append(f"{code} - {name}")  
        else:
            college_options.append(college_key)

    update_window = tk.Toplevel(window)
    update_window.geometry("450x300")
    update_window.title("Update Student")
    update_window.config(bg="#800000")
    
    update_window.transient(window)
    update_window.grab_set()
    
    vcmd_char = update_window.register(lambda current, inserted: validate_char(current, inserted))
    vcmd_int = update_window.register(validate_int)
    vcmd_idno = update_window.register(validate_idno)

    label_idno = tk.Label(update_window, text="ID#:", bg="#800000", fg="white")
    label_idno.grid(row=1, column=0)
    label_idno = tk.Label(update_window, text="(ex. YYYY-NNNN)", bg="#800000", fg="white")
    label_idno.grid(row=1, column=2, sticky="w")
    entry_idno = tk.Entry(update_window, validate="key", validatecommand=(vcmd_idno, '%P'), width=40)
    entry_idno.insert(0, current_values[0])
    entry_idno.grid(row=1, column=1, sticky="w")

    label_name = tk.Label(update_window, text="First Name:", bg="#800000", fg="white")
    label_name.grid(row=2, column=0)
    entry_firstname = tk.Entry(update_window, validate="key", validatecommand=(vcmd_char, '%P', '%S'), width=40)
    entry_firstname.insert(0, current_values[1])
    entry_firstname.grid(row=2, column=1,sticky="w")

    label_lastname = tk.Label(update_window, text="Last Name:", bg="#800000", fg="white")
    label_lastname.grid(row=3, column=0)
    entry_lastname = tk.Entry(update_window, validate="key", validatecommand=(vcmd_char, '%P', '%S'), width=40)
    entry_lastname.insert(0, current_values[2])
    entry_lastname.grid(row=3, column=1, sticky="w")

    label_age = tk.Label(update_window, text="Age:", bg="#800000", fg="white")
    label_age.grid(row=4, column=0)
    entry_age = tk.Entry(update_window, validate="key", validatecommand=(vcmd_int, '%S'))
    entry_age.insert(0, current_values[3])
    entry_age.grid(row=4, column=1, sticky="w")

    
    label_gender = tk.Label(update_window, text="Gender:", bg="#800000", fg="white")
    label_gender.grid(row=5, column=0)
    gender_var = tk.StringVar(update_window)
    gender_choices = ["Male", "Female", "Others"]
    gender_dropdown = ttk.Combobox(update_window, textvariable=gender_var, values=gender_choices, state='readonly', width=17)  # Increased width to show full names
    gender_dropdown.grid(row=5, column=1, sticky="w")
    gender_var.set(current_values[4]) 

   
    label_yearlevel = tk.Label(update_window, text="Year Level:", bg="#800000", fg="white")
    label_yearlevel.grid(row=6, column=0)
    yearlevel_var = tk.StringVar(update_window)
    yearlevel_choices = ["1st", "2nd", "3rd", "4th", "5+"]
    yearlevel_dropdown = ttk.Combobox(update_window, textvariable=yearlevel_var, values=yearlevel_choices, state='readonly', width=17)  # Increased width to show full names
    yearlevel_dropdown.grid(row=6, column=1, sticky="w")
    yearlevel_var.set(current_values[5])  

   
    label_college = tk.Label(update_window, text="College:", bg="#800000", fg="white")
    label_college.grid(row=7, column=0)
    college_var = tk.StringVar(update_window)
    college_options = [k for k in college_courses if k != "_orphaned_"]
    college_dropdown = ttk.Combobox(update_window, textvariable=college_var, values=college_options, state='readonly', width=40)  # Increased width to show full names
    college_dropdown.grid(row=7, column=1)
    college_dropdown.bind("<<ComboboxSelected>>", update_courses)
  
    college_abbr = current_values[6]
    full_college_key = next((k for k in college_courses if k.startswith(f"{college_abbr} -")), None)
    if full_college_key:
        college_var.set(full_college_key)
    elif college_abbr == "N/A":
        college_var.set("N/A")
    else:
        college_var.set('')

    label_course = tk.Label(update_window, text="Course:", bg="#800000", fg="white")
    label_course.grid(row=8, column=0)
    course_var = tk.StringVar(update_window)
    course_dropdown = ttk.Combobox(update_window, textvariable=course_var, values=[], state='readonly', width=40)
    course_dropdown.grid(row=8, column=1)

    update_courses()

    course_code = current_values[7]
    full_course_name = next(
        (course for course in college_courses.get(college_var.get(), []) if course.startswith(course_code)),
        None
    )
    if full_course_name:
        course_var.set(full_course_name)
    elif course_code == "N/A":
        course_var.set("N/A")
    else:
        course_var.set('')

    button_save = tk.Button(update_window, text="Save Changes", bg="#d9a300", command=save_changes)
    button_save.grid(row=9, column=0, columnspan=2, pady=10)


def display_current_page():
    global current_page, total_pages
    
    
    table.delete(*table.get_children())
    
    
    filtered_students = get_filtered_students()
    total_pages = max(1, (len(filtered_students) + rows_per_page - 1) // rows_per_page)
    current_page = min(current_page, total_pages)
    
    
    start_idx = (current_page - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, len(filtered_students))
    
    
    for student in filtered_students[start_idx:end_idx]:
        table.insert("", "end", values=student)
    
    
    page_info.config(text=f"Page {current_page} of {total_pages} | Total: {len(filtered_students)} students")
    
    
    btn_first.config(state="normal" if current_page > 1 else "disabled")
    btn_prev.config(state="normal" if current_page > 1 else "disabled")
    btn_next.config(state="normal" if current_page < total_pages else "disabled")
    btn_last.config(state="normal" if current_page < total_pages else "disabled")


def clear_table():
    global all_students
    confirm = messagebox.askyesno("Clear Data Confirmation", "Are you sure you want to clear all data?")
    if confirm:
        
        all_students = []
        
        
        for item in table.get_children():
            table.delete(item)
        
        
        try:
            with open(CSV_FILE, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)  
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear data: {str(e)}")
        
        entry_search.delete(0, 'end')


all_students = []

current_page = 1
rows_per_page = 20
total_pages = 1

def calculate_total_pages():
    global total_pages
    filtered_students = get_filtered_students()
    total_pages = max(1, (len(filtered_students) + rows_per_page - 1) // rows_per_page)
    return total_pages

def get_filtered_students():
    search_text = entry_search.get().strip().lower()
    search_by = search_var.get()  

    if not search_text:
        return all_students

    filtered = []
    for student in all_students:
        if search_by == "ID#" and search_text in str(student[0]).lower():
            filtered.append(student)
        elif search_by == "First Name" and search_text in str(student[1]).lower():
            filtered.append(student)
        elif search_by == "Last Name" and search_text in str(student[2]).lower():
            filtered.append(student)
    return filtered

def go_to_page(page_num):
    global current_page, total_pages
    if 1 <= page_num <= total_pages:
        current_page = page_num
        refresh_table()

def search_student(event=None):
    global current_page
    current_page = 1  
    refresh_table()  


def save_to_csv():
    try:
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)  
            writer.writerows(all_students)  
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data: {str(e)}")


def load_initial_data():
    global all_students
    all_students = []
    
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
        return
    
    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            
            for row in reader:
                if not row:
                    continue
                if row[0] == "Colleges and Courses":
                    break
                if len(row) == len(columns):
                    all_students.append(tuple(row))
        
        refresh_table()
        
    except Exception as e:
        print(f"Load error: {e}")
        messagebox.showerror("Load Error", f"Failed to load data: {str(e)}")

def validate_idno(char):
    return re.match(r'^\d{0,4}(-\d{0,4})?$', char) is not None

vcmd_idno_main = window.register(validate_idno)

icon = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__), 'student.png'))
window.iconphoto(True, icon)
window.config(bg="#800000")


control_frame = tk.Frame(window, bg="#800000")
control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

button_add = tk.Button(control_frame, text="Add Student", bg="#7d6a69", fg="white", command=add_student)
button_add.grid(row=0, column=0, pady=5)

button_delete = tk.Button(control_frame, text="Delete Student", bg="#7d6a69", fg="white", command=delete_student)
button_delete.grid(row=1, column=0, pady=5)

button_update = tk.Button(control_frame, text="Update Student", bg="#7d6a69", fg="white", command=update_student)
button_update.grid(row=2, column=0, pady=5)

columns = ("ID#","First Name", "Last Name", "Age", "Gender", "Year Level", "College", "Course")


label_search = tk.Label(control_frame, text="Search by:", bg="#800000", fg="white")
label_search.grid(row=3, column=0, pady=5)

search_var = tk.StringVar(value="ID#")
search_by = ttk.Combobox(control_frame, 
                        textvariable=search_var,
                        values=["ID#", "First Name", "Last Name"],
                        state='readonly',
                        width=15)
search_by.grid(row=4, column=0, pady=2)

entry_search = tk.Entry(control_frame, width=20)
entry_search.bind("<KeyRelease>", search_student)
entry_search.grid(row=5, column=0, pady=5)

button_clear = tk.Button(control_frame, text="Clear Data", bg="#7d6a69", fg="white", command=clear_table)
button_clear.grid(row=6, column=0, pady=50)

class StudentTableRefreshWrapper:
    def refresh_table(self):
        refresh_table()

shared_refresh_ref = StudentTableRefreshWrapper()

button_manage_colleges = tk.Button(control_frame, text="Manage Colleges", 
                                 bg="#7d6a69", fg="white", 
                                 command=lambda: CollegeManager(window, student_table_ref=shared_refresh_ref))
button_manage_colleges.grid(row=7, column=0, pady=5)

button_manage_courses = tk.Button(control_frame, text="Manage Courses", 
                                bg="#7d6a69", fg="white", 
                                command=lambda: CourseManager(window,college_courses, student_table_ref=shared_refresh_ref))
button_manage_courses.grid(row=8, column=0, pady=5)


table_frame = tk.Frame(window, bg="#800000")
table_frame.config(height=300)  
table_frame.grid(row=0, column=1, padx=10, pady=0, sticky="nsew")  


window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=1)


table = ttk.Treeview(table_frame, columns=columns, show="headings")
table.heading("ID#", text="ID#")
table.heading("First Name", text="First Name")
table.heading("Last Name", text="Last Name")
table.heading("Age", text="Age")
table.heading("Gender", text="Gender")
table.heading("Year Level", text="Year Level")
table.heading("College", text="College")
table.heading("Course", text="Course")


for col in columns:
    table.column(col, width=100, stretch=True)


table.grid(row=2, column=0, sticky="nsew", pady=0)  

pagination_frame = tk.Frame(table_frame, bg="#800000")
pagination_frame.grid(row=3, column=0, sticky="ew", columnspan=2)  

btn_first = tk.Button(pagination_frame, text="<<", command=lambda: go_to_page(1),
                     bg="#7d6a69", fg="white")
btn_first.pack(side=tk.LEFT, padx=5)

btn_prev = tk.Button(pagination_frame, text="<", command=lambda: go_to_page(current_page - 1),
                    bg="#7d6a69", fg="white")
btn_prev.pack(side=tk.LEFT, padx=5)

page_info = tk.Label(pagination_frame, text="Page 1 of 1", bg="#800000", fg="white")
page_info.pack(side=tk.LEFT, padx=10)

btn_next = tk.Button(pagination_frame, text=">", command=lambda: go_to_page(current_page + 1),
                    bg="#7d6a69", fg="white")
btn_next.pack(side=tk.LEFT, padx=5)

btn_last = tk.Button(pagination_frame, text=">>", command=lambda: go_to_page(total_pages),
                    bg="#7d6a69", fg="white")
btn_last.pack(side=tk.LEFT, padx=5)

table_frame.grid_rowconfigure(0, weight=0)  
table_frame.grid_rowconfigure(1, weight=0)  
table_frame.grid_rowconfigure(2, weight=1)  
table_frame.grid_rowconfigure(3, weight=0)

load_initial_data()

def clear_selection(event):
    for item in table.selection():
        table.selection_remove(item)

table.bind("<Double-1>", clear_selection)

def adjust_rows_per_page(event=None):
    global rows_per_page, current_page
    
    
    table_height = table_frame.winfo_height()
    row_height = 25  
    header_height = 25  
    pagination_height = 35  
    
    
    available_height = table_height - header_height - pagination_height
    new_rows_per_page = max(1, available_height // row_height)
    
    
    if new_rows_per_page != rows_per_page:
        rows_per_page = new_rows_per_page
        refresh_table()

window.bind("<Configure>", adjust_rows_per_page)

initialize_data()

class StudentFilterSort:
    def __init__(self, main_window, table_frame):
        self.filter_frame = tk.Frame(table_frame, bg="#800000")
        self.filter_frame.grid(row=0, column=0, sticky="nsew", pady=0)  
        
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(2, weight=1)
        table_frame.grid_rowconfigure(3, weight=0)
        
        tk.Label(self.filter_frame, text="Filter by:", 
                bg="#800000", fg="white").pack(side=tk.LEFT, padx=(10,5))
        
        self.college_var = tk.StringVar()
        valid_colleges = [k for k in college_courses if k != "_orphaned_"]
        self.college_filter = ttk.Combobox(
            self.filter_frame,
            textvariable=self.college_var,
            values=["All Colleges"] + valid_colleges,
            state='readonly', width=20)
        self.college_filter.set("All Colleges")
        self.college_filter.pack(side=tk.LEFT, padx=2)
        
        self.year_var = tk.StringVar()
        self.year_filter = ttk.Combobox(self.filter_frame, 
                                      textvariable=self.year_var,
                                      values=["All Years", "1st", "2nd", "3rd", "4th", "5+"],
                                      state='readonly',
                                      width=10)
        self.year_filter.set("All Years")
        self.year_filter.pack(side=tk.LEFT, padx=2)
        
        self.gender_var = tk.StringVar()
        self.gender_filter = ttk.Combobox(self.filter_frame, 
                                        textvariable=self.gender_var,
                                        values=["All Genders", "Male", "Female", "Others"],
                                        state='readonly',
                                        width=10)
        self.gender_filter.set("All Genders")
        self.gender_filter.pack(side=tk.LEFT, padx=2)
        
        tk.Button(self.filter_frame, text="Apply Filters", 
                 bg="#7d6a69", fg="white",
                 command=self.apply_filters).pack(side=tk.LEFT, padx=2)
        tk.Button(self.filter_frame, text="Clear Filters", 
                 bg="#7d6a69", fg="white",
                 command=self.clear_filters).pack(side=tk.LEFT, padx=2)
        
        self.sort_frame = tk.Frame(table_frame, bg="#800000")
        self.sort_frame.grid(row=1, column=0, sticky="nsew", pady=0)  
        
        tk.Label(self.sort_frame, text="Sort by:", 
                bg="#800000", fg="white").pack(side=tk.LEFT, padx=(10,5))
        
        self.primary_sort = ttk.Combobox(self.sort_frame, 
                                       values=["Original Order", "ID#", "First Name", "Last Name", 
                                              "Age", "Gender", "Year Level", "College", "Course"],
                                       state="readonly",
                                       width=15)
        self.primary_sort.set("Original Order")
        self.primary_sort.pack(side=tk.LEFT, padx=2)
        
        self.sort_order = ttk.Combobox(self.sort_frame, 
                                     values=["Ascending", "Descending"],
                                     state="readonly",
                                     width=10)
        self.sort_order.set("Ascending")
        self.sort_order.pack(side=tk.LEFT, padx=2)
        
        tk.Button(self.sort_frame, text="Apply Sort", 
                 bg="#7d6a69", fg="white",
                 command=self.apply_sort).pack(side=tk.LEFT, padx=2)

    def apply_filters(self):
        global all_students, current_page, filtered_students
        
        filtered_students = list(all_students)  
        
        try:
            with open(CSV_FILE, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  
                filtered_students = [tuple(row) for row in reader 
                                  if row and len(row) == len(columns)]
            
            selected_college = self.college_var.get()
            selected_year = self.year_var.get()
            selected_gender = self.gender_var.get()
            
            if selected_college != "All Colleges":
                filtered_students = [s for s in filtered_students 
                                   if s[6].startswith(selected_college.split(' - ')[0])]
            
            if selected_year != "All Years":
                filtered_students = [s for s in filtered_students 
                                   if s[5] == selected_year]
            
            if selected_gender != "All Genders":
                filtered_students = [s for s in filtered_students 
                                   if s[4] == selected_gender]
            
            
            
            current_page = 1
            refresh_table(filtered_students)
            
        except Exception as e:
            print(f"Error applying filters: {e}")
            messagebox.showerror("Error", "Failed to apply filters")
    
    def clear_filters(self):
        global displayed_students
        self.college_filter.set("All Colleges")
        self.year_filter.set("All Years")
        self.gender_filter.set("All Genders")
        
        global all_students
        try:
            with open(CSV_FILE, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  
                all_students = [tuple(row) for row in reader 
                              if row and len(row) == len(columns)]
            refresh_table()
        except Exception as e:
            print(f"Error restoring original data: {e}")
    
    def apply_sort(self):
        global filtered_students

        sort_by = self.primary_sort.get()
        reverse = self.sort_order.get() == "Descending"

        if sort_by == "Original Order":
            refresh_table(filtered_students)
            return

        index_map = {
            "ID#": 0, "First Name": 1, "Last Name": 2, 
            "Age": 3, "Gender": 4, "Year Level": 5, 
            "College": 6, "Course": 7
        }

        index = index_map.get(sort_by, 0)

        sorted_list = sorted(filtered_students, key=lambda s: s[index], reverse=reverse)
        refresh_table(sorted_list)
        
    def refresh_filter_values(self):
        current_college = self.college_var.get()
        
        new_college_values = ["All Colleges"] + list(college_courses.keys())
        self.college_filter['values'] = new_college_values
        
        if current_college in new_college_values:
            self.college_filter.set(current_college)
        else:
            self.college_filter.set("All Colleges")


student_filter_sort = StudentFilterSort(window, table_frame)


refresh_table()
window.mainloop()



